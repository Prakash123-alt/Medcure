"""
RAG Quality Verification Script.
Tests that the aiims_rag_node retrieval improvements are working correctly.

Runs 3 clinical queries and checks:
1. Results have distance < 0.45 (relevance threshold)
2. Results don't contain noise keywords (preface, copyright, etc.)
3. Results contain actual clinical content

Usage: python test_rag_quality.py
"""
import asyncio
import os
import sys
import json
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from medical_ai_agent.database import init_db_pool, close_db_pool, get_db_connection
from medical_ai_agent.config import config
from langchain_google_vertexai import VertexAIEmbeddings

DISTANCE_THRESHOLD = 0.45

NOISE_KEYWORDS = [
    "standard treatment guidelines", "first edition", "message from",
    "preface", "foreword", "acknowledgement", "table of contents",
    "copyright", "all rights reserved", "disclaimer", "published by",
    "isbn", "contributors", "committee",
]

TEST_QUERIES = [
    "Clinical management and treatment guidelines for: Type 2 Diabetes",
    "Clinical guidelines for: hypertension management and treatment",
    "Clinical guidelines for: fever and headache in child",
]


async def run_query(conn, embeddings, query_text):
    """Run a single RAG query and return results with distances."""
    query_vector = embeddings.embed_query(query_text)
    query_np = np.array(query_vector, dtype=np.float32)
    
    results = await conn.fetch(
        "SELECT content, embedding <=> $1 as distance FROM aiims_guidelines ORDER BY embedding <=> $1 LIMIT 5",
        query_np
    )
    
    return [{"distance": float(row['distance']), "content": row['content']} for row in results]


async def main():
    await init_db_pool()
    
    try:
        embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
        all_results = {}
        all_passed = True
        
        async with get_db_connection() as conn:
            # Get total row count
            row_count = await conn.fetchval("SELECT COUNT(*) FROM aiims_guidelines")
            print(f"\n[INFO] Total rows in aiims_guidelines: {row_count}")
            print(f"[INFO] Distance threshold: {DISTANCE_THRESHOLD}")
            print(f"{'='*70}\n")
            
            for query in TEST_QUERIES:
                print(f"[QUERY] \"{query}\"")
                results = await run_query(conn, embeddings, query)
                
                good_results = []
                noisy_results = []
                
                for i, r in enumerate(results):
                    dist = r['distance']
                    snippet = r['content'][:80].replace('\n', ' ')
                    
                    # Check distance
                    passes_threshold = dist < DISTANCE_THRESHOLD
                    
                    # Check for noise
                    is_noisy = any(kw in r['content'].lower() for kw in NOISE_KEYWORDS)
                    
                    marker = "[OK]" if (passes_threshold and not is_noisy) else "[FAIL]"
                    print(f"  {marker} Match {i+1}: dist={dist:.4f} | {snippet}...")
                    
                    if passes_threshold and not is_noisy:
                        good_results.append(r)
                    else:
                        if is_noisy:
                            noisy_results.append(r)
                
                # Verdict
                if good_results:
                    print(f"  [PASS] {len(good_results)} relevant results passed\n")
                else:
                    print(f"  [WARN] No results passed threshold -- retrieved content may be irrelevant\n")
                    all_passed = False
                
                if noisy_results:
                    print(f"  [WARN] {len(noisy_results)} results contained noise keywords -- data needs cleaning\n")
                    all_passed = False
                
                all_results[query] = {
                    "results": results,
                    "good_count": len(good_results),
                    "noisy_count": len(noisy_results),
                }
        
        # Save results to file
        output_path = os.path.join(os.path.dirname(__file__), "rag_quality_results.json")
        with open(output_path, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[INFO] Full results saved to: {output_path}")
        
        # Final verdict
        print(f"\n{'='*70}")
        if all_passed:
            print("[PASS] ALL QUERIES PASSED -- RAG retrieval quality looks good!")
        else:
            print("[WARN] SOME QUERIES HAD ISSUES -- review results above")
            print("   Tip: Run 'python clean_noisy_rows.py' to remove noisy data")
        print(f"{'='*70}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[ERROR] {e}")
    finally:
        await close_db_pool()


if __name__ == "__main__":
    asyncio.run(main())
