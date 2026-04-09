"""Quick embedding test using the new _GoogleAIEmbeddings wrapper"""
import asyncio, sys, os, warnings
warnings.filterwarnings("ignore")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

os.chdir(r"E:\Prototypes\Nithin\curemate\medcure_GDGE")

async def main():
    from medical_ai_agent.nodes.clinical_brain import get_embeddings, get_cached_embedding
    emb = get_embeddings()

    # Test embed_query
    vec = emb.embed_query("Type 2 diabetes metformin treatment")
    print(f"embed_query  → dim={len(vec)}, first_3={vec[:3]}")

    # Test aembed_documents (batch)
    vecs = await emb.aembed_documents(["patient has hypertension", "creatinine is elevated"])
    print(f"aembed_documents → {len(vecs)} vecs, dim={len(vecs[0])}")

    # Test cached embedding
    ce = await get_cached_embedding("Type 2 diabetes metformin treatment")
    print(f"get_cached_embedding → dim={len(ce)}")

    print("\nPASS: Embeddings using Google AI Studio API key ✅")

asyncio.run(main())
