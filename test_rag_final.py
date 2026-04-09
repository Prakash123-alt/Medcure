import asyncio
import os
import sys
import json

# Add project root to sys.path
sys.path.append("c:\\Users\\Yasin.Dhalait\\Documents\\GitHub\\medcure_GDGE")

import logging

# Set up logging to file
log_path = "c:\\Users\\Yasin.Dhalait\\Documents\\GitHub\\medcure_GDGE\\rag_test.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def test_rag_retrieval(query_text):
    await init_db_pool()
    os.environ['GOOGLE_API_KEY'] = config.GOOGLE_API_KEY
    
    try:
        logger.info(f"--- RAG Retrieval Test ---")
        logger.info(f"Query: '{query_text}'")
        
        logger.info("Starting embedding generation...")
        embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
        query_vector = embeddings.embed_query(query_text)
        logger.info(f"Generated embedding. Dim: {len(query_vector)}")
        
        formatted_query_vector = f"[{','.join(map(str, query_vector))}]"
        
        logger.info("Connecting to DB...")
        async with get_db_connection() as conn:
            logger.info("Running vector search...")
            results = await conn.fetch("""
                SELECT content, embedding <=> $1::vector as distance
                FROM aiims_guidelines 
                ORDER BY distance
                LIMIT 5
            """, formatted_query_vector)
            
            results_to_save = []
            if results:
                print(f"Found {len(results)} matches.")
                for i, row in enumerate(results):
                    results_to_save.append({
                        "match_index": i + 1,
                        "distance": float(row['distance']),
                        "content": str(row['content'])
                    })
            
            output_path = "c:\\Users\\Yasin.Dhalait\\Documents\\GitHub\\medcure_GDGE\\rag_results_final.json"
            with open(output_path, "w") as f:
                json.dump(results_to_save, f, indent=2)
            print(f"Results saved to {output_path}")
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
    finally:
        await close_db_pool()

if __name__ == "__main__":
    test_query = "symptoms and treatment for Type 2 Diabetes"
    asyncio.run(test_rag_retrieval(test_query))
