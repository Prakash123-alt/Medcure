"""
GraphRAG ETL Pipeline: AIIMS Guidelines to Neo4j.

This script fetches raw text chunks from the PostgreSQL `aiims_guidelines` table,
uses Gemini to extract medical entities (Diseases, Drugs, Symptoms) and relationships,
and ingests them into a Neo4j Knowledge Graph.
"""
import asyncio
import os
import sys
import json
import logging
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from medical_ai_agent.database import init_db_pool, close_db_pool, get_db_connection
from medical_ai_agent.knowledge_graph import neo4j_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# --- 1. Define the Output Schema for Gemini Extraction ---

class Disease(BaseModel):
    name: str = Field(description="Name of the disease or medical condition")
    category: str = Field(description="Broad category, e.g., 'Cardiovascular', 'Endocrine'")

class Drug(BaseModel):
    name: str = Field(description="Generic name of the drug/medicine")
    drug_class: str = Field(default="Unknown", description="Class of the drug, e.g., 'Beta Blocker'")

class Symptom(BaseModel):
    name: str = Field(description="Name of the symptom")

class Condition(BaseModel):
    name: str = Field(description="Patient condition like 'Pregnancy', 'Renal Failure', 'Elderly'")

class Relationship(BaseModel):
    source_entity: str = Field(description="Name of the source entity (must exactly match a drug, disease, or symptom name above)")
    source_type: str = Field(description="Type of the source entity: 'Disease', 'Drug', 'Symptom', or 'Condition'")
    target_entity: str = Field(description="Name of the target entity (must exactly match a drug, disease, or symptom name above)")
    target_type: str = Field(description="Type of the target entity: 'Disease', 'Drug', 'Symptom', or 'Condition'")
    relationship_type: str = Field(description="One of: 'TREATED_BY', 'HAS_SYMPTOM', 'CONTRAINDICATED_IN', 'CAUSES_SIDE_EFFECT', 'INTERACTS_WITH'")
    context: str = Field(default="", description="Any brief context, e.g., 'first-line therapy', 'max dose 500mg'")

class KnowledgeExtraction(BaseModel):
    diseases: List[Disease] = Field(default_factory=list)
    drugs: List[Drug] = Field(default_factory=list)
    symptoms: List[Symptom] = Field(default_factory=list)
    conditions: List[Condition] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)


# --- 2. Extraction Pipeline ---

async def extract_entities_from_chunk(llm, chunk_text: str) -> KnowledgeExtraction:
    """Use Gemini to extract structured knowledge from a text chunk."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert medical data extractor. 
        Analyze the following text from a clinical guideline (AIIMS Standard Treatment Guidelines).
        Extract all Diseases, Drugs, Symptoms, and Patient Conditions mentioned.
        Then, extract the relationships between them. 
        
        Valid relationships are ONLY:
        - (Disease) -TREATED_BY-> (Drug)
        - (Disease) -HAS_SYMPTOM-> (Symptom)
        - (Drug) -CONTRAINDICATED_IN-> (Condition)
        - (Drug) -CAUSES_SIDE_EFFECT-> (Symptom)
        - (Drug) -INTERACTS_WITH-> (Drug)
        
        If a text doesn't contain medical entities (e.g., table of contents, preamble), return empty lists.
        Be precise and use generic drug names where possible."""),
        ("human", "{text}")
    ])
    
    chain = prompt | llm.with_structured_output(KnowledgeExtraction)
    
    try:
        # LLMs can sometimes fail structured output parsing, wrap in try-except
        result = await chain.ainvoke({"text": chunk_text})
        return result
    except Exception as e:
        logger.warning(f"Extraction failed for a chunk: {str(e)[:100]}")
        return KnowledgeExtraction()


# --- 3. Neo4j Ingestion Pipeline ---

async def ingest_into_neo4j(driver, extraction: KnowledgeExtraction, source_chunk_id: int):
    """Insert extracted entities and relationships into Neo4j using Cypher MERGE."""
    
    async def _execute_merge(tx):
        # 1. Create Guideline Chunk Node
        await tx.run("""
            MERGE (c:GuidelineChunk {chunk_id: $chunk_id})
        """, chunk_id=source_chunk_id)
        
        # 2. Merge Diseases and link to Chunk
        for disease in extraction.diseases:
            await tx.run("""
                MERGE (d:Disease {name: toLower($name)})
                SET d.category = $category
                WITH d
                MATCH (c:GuidelineChunk {chunk_id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(d)
            """, name=disease.name, category=disease.category, chunk_id=source_chunk_id)
            
        # 3. Merge Drugs and link to Chunk
        for drug in extraction.drugs:
            await tx.run("""
                MERGE (dr:Drug {name: toLower($name)})
                SET dr.class = $drug_class
                WITH dr
                MATCH (c:GuidelineChunk {chunk_id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(dr)
            """, name=drug.name, drug_class=drug.drug_class, chunk_id=source_chunk_id)
            
        # 4. Merge Symptoms
        for symptom in extraction.symptoms:
            await tx.run("""
                MERGE (s:Symptom {name: toLower($name)})
                WITH s
                MATCH (c:GuidelineChunk {chunk_id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(s)
            """, name=symptom.name, chunk_id=source_chunk_id)
            
        # 5. Merge Conditions
        for condition in extraction.conditions:
            await tx.run("""
                MERGE (cond:Condition {name: toLower($name)})
                WITH cond
                MATCH (c:GuidelineChunk {chunk_id: $chunk_id})
                MERGE (c)-[:MENTIONS]->(cond)
            """, name=condition.name, chunk_id=source_chunk_id)
            
        # 6. Merge Relationships
        for rel in extraction.relationships:
            if not rel.source_entity or not rel.target_entity:
                continue
                
            # Dynamic Cypher generation for relationships since label parameterization isn't supported
            # We enforce label safety through the strict prompt choices
            src_label = rel.source_type
            tgt_label = rel.target_type
            rel_type = rel.relationship_type
            
            # Map the allowed list just to be safe against prompt injection/hallucination
            allowed_labels = {"Disease", "Drug", "Symptom", "Condition"}
            allowed_rels = {"TREATED_BY", "HAS_SYMPTOM", "CONTRAINDICATED_IN", "CAUSES_SIDE_EFFECT", "INTERACTS_WITH"}
            
            if src_label in allowed_labels and tgt_label in allowed_labels and rel_type in allowed_rels:
                query = f"""
                    MATCH (src:{src_label} {{name: toLower($src_name)}})
                    MATCH (tgt:{tgt_label} {{name: toLower($tgt_name)}})
                    MERGE (src)-[r:{rel_type}]->(tgt)
                    SET r.context = $context, r.source_chunk_id = $chunk_id
                """
                await tx.run(query, src_name=rel.source_entity, tgt_name=rel.target_entity, 
                             context=rel.context, chunk_id=source_chunk_id)

    async with driver.session() as session:
        await session.execute_write(_execute_merge)


# --- 4. Main ETL Execution ---

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build Medical Knowledge Graph from AIIMS PDF")
    parser.add_argument("--limit", type=int, default=10, help="Number of chunks to process (for testing)")
    parser.add_argument("--offset", type=int, default=0, help="Offset for chunks")
    args = parser.parse_args()
    
    logger.info("Initializing Database Connections...")
    await init_db_pool()
    neo4j_async_driver = await neo4j_db.connect_async()
    
    # Initialize Neo4j schema constraints (needs sync driver)
    neo4j_db.initialize_schema()
    
    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    try:
        async with get_db_connection() as conn:
            # 1. Fetch text chunks from postgres
            rows = await conn.fetch(
                "SELECT id, content FROM aiims_guidelines ORDER BY id LIMIT $1 OFFSET $2",
                args.limit, args.offset
            )
            
            # --- SKIP ALREADY PROCESSED CHUNKS ---
            async with neo4j_async_driver.session() as session:
                result = await session.run("MATCH (c:GuidelineChunk) RETURN c.chunk_id")
                existing_ids = {row[0] for row in await result.values()}
            
            initial_count = len(rows)
            rows = [r for r in rows if r['id'] not in existing_ids]
            logger.info(f"Skipped {initial_count - len(rows)} already processed chunks. Remaining: {len(rows)}")
            
            if not rows:
                logger.info("All requested chunks are already processed. Exiting.")
                return
            
            logger.info(f"Loaded {len(rows)} chunks. Beginning extraction pipeline (Parallel, 5 concurrent)...")
            
            semaphore = asyncio.Semaphore(5)
            
            async def process_item(i, row):
                nonlocal total_diseases, total_drugs, total_rels
                async with semaphore:
                    chunk_id = row['id']
                    content = row['content']
                    
                    if len(content) < 50:
                        return
                        
                    logger.info(f"Processing chunk {i+1}/{len(rows)} (ID: {chunk_id})...")
                    extraction = await extract_entities_from_chunk(llm, content)
                    
                    if extraction.diseases or extraction.drugs:
                        await ingest_into_neo4j(neo4j_async_driver, extraction, chunk_id)
                        logger.info(f"  ID:{chunk_id} -> Ingested (D:{len(extraction.diseases)} Dr:{len(extraction.drugs)} Rels:{len(extraction.relationships)}) ✅")
                        total_diseases += len(extraction.diseases)
                        total_drugs += len(extraction.drugs)
                        total_rels += len(extraction.relationships)
                    else:
                        logger.info(f"  ID:{chunk_id} -> No clinical data.")

            total_diseases = 0
            total_drugs = 0
            total_rels = 0
            
            tasks = [process_item(i, row) for i, row in enumerate(rows)]
            await asyncio.gather(*tasks)
                    
            logger.info(f"ETL Complete! Extracted ~{total_diseases} diseases, ~{total_drugs} drugs, and ~{total_rels} relationships.")
            
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await close_db_pool()
        await neo4j_db.close_async()


if __name__ == "__main__":
    asyncio.run(main())
