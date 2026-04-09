"""
Quick connectivity test for all services.
Run: python _connectivity_test.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_postgres():
    print("--- Testing PostgreSQL ---")
    try:
        import asyncpg
        pg_uri = os.getenv("PG_URI")
        conn = await asyncpg.connect(pg_uri)
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        )
        row_counts = {}
        for t in tables[:8]:  # sample first 8 tables
            cnt = await conn.fetchval(f"SELECT COUNT(*) FROM {t['tablename']}")
            row_counts[t["tablename"]] = cnt
        await conn.close()
        print(f"  OK — Tables: {row_counts}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_neo4j():
    print("\n--- Testing Neo4j ---")
    try:
        from neo4j import AsyncGraphDatabase
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        pw = os.getenv("NEO4J_PASSWORD")
        driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
        async with driver.session() as session:
            result = await session.run("MATCH (n) RETURN count(n) as cnt LIMIT 1")
            record = await result.single()
            cnt = record["cnt"]
            # Get distinct label counts
            result2 = await session.run(
                "CALL db.labels() YIELD label RETURN label LIMIT 20"
            )
            labels = [r["label"] async for r in result2]
        await driver.close()
        print(f"  OK — Total nodes: {cnt} | Labels: {labels}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_gemini():
    print("\n--- Testing Gemini LLM ---")
    try:
        from medical_ai_agent.llm_utils import get_gemini_llm
        from langchain_core.messages import HumanMessage
        llm = get_gemini_llm(model_name="gemini-2.5-flash", temperature=0)
        resp = await llm.ainvoke([HumanMessage(content="Reply with only the word PONG")])
        print(f"  OK — Response: {resp.content.strip()[:80]}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_deepseek():
    print("\n--- Testing DeepSeek ---")
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
        )
        resp = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Reply with only the word PONG"}],
            max_tokens=10,
            temperature=0,
        )
        content = resp.choices[0].message.content.strip()
        print(f"  OK — Response: {content}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def test_end_to_end():
    print("\n--- Testing End-to-End Agent (L1 Casual) ---")
    try:
        from medical_ai_agent.graph import build_graph
        app = build_graph()
        initial_state = {
            "image_path": None,
            "food_image_path": None,
            "patient_id": "test_user_001",
            "session_id": "test_session_001",
            "user_input": "Hello, how are you?",
            "chat_history": [{"role": "user", "content": "Hello, how are you?"}],
            "persona_type": "Coach",
            "engagement_score": 60,
            "research_iteration_count": 0,
            "user_sentiment": "neutral",
            "weather_context": "Normal",
            "errors": [],
            "messages": [],
            "context_summary": "",
            "long_term_memories": "",
        }
        import asyncio
        final_state = await asyncio.wait_for(
            app.ainvoke(initial_state, config={"configurable": {"thread_id": "test-001"}}),
            timeout=60
        )
        msg = final_state.get("final_message", "(no message)")
        print(f"  OK — Final message ({len(msg)} chars):\n  {msg[:200]}")
        errors = final_state.get("errors", [])
        if errors:
            print(f"  Errors in state: {errors}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 55)
    print("  Sister Nani — Full Connectivity & Agent Test")
    print("=" * 55)

    pg_ok = await test_postgres()
    neo4j_ok = await test_neo4j()
    gemini_ok = await test_gemini()
    deepseek_ok = await test_deepseek()

    if gemini_ok:
        e2e_ok = await test_end_to_end()
    else:
        e2e_ok = False
        print("\n--- Skipping E2E test (Gemini unavailable) ---")

    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)
    for name, ok in [
        ("PostgreSQL", pg_ok),
        ("Neo4j", neo4j_ok),
        ("Gemini LLM", gemini_ok),
        ("DeepSeek", deepseek_ok),
        ("End-to-End Agent", e2e_ok),
    ]:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
