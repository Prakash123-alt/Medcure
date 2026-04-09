"""Quick test for build_graph_with_postgres()"""
import asyncio, sys, warnings
warnings.filterwarnings("ignore")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

async def main():
    from medical_ai_agent.graph import build_graph_with_postgres
    print("Building graph with PostgreSQL checkpointer...")
    app, conn = await asyncio.wait_for(build_graph_with_postgres(), timeout=20)
    print(f"Graph nodes: {len(app.nodes)}")
    await conn.close()
    print("PASS: PostgreSQL checkpointer OK")

asyncio.run(main())
