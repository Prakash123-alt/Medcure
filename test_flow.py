import os
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

from medical_ai_agent.graph import build_graph

graph = build_graph()

async def test_query(test_name: str, message: str):
    print(f"\n==================================================")
    print(f"TESTING: {test_name}")
    print(f"QUERY: '{message}'")
    print(f"==================================================")

    initial_state = {
        "image_path": None,
        "food_image_path": None,
        "patient_id": "test-user-001",
        "session_id": "test-session",
        "user_input": message,
        "chat_history": [{"role": "user", "content": message}],
        "persona_type": "Companion",
        "engagement_score": 50,
        "research_iteration_count": 0,
        "long_term_memories": "",
        "user_sentiment": "neutral",
        "errors": [],
    }

    try:
        cfg = {"configurable": {"thread_id": f"test_{test_name.replace(' ', '_')}"}}
        result = await graph.ainvoke(initial_state, config=cfg)
        print("\n--- RESULTS ---")
        print(f"Triage Level:  {result.get('triage_level')}")
        print(f"Triage Reason: {result.get('triage_reason')}")
        print(f"Final Message:\n{result.get('final_message')}")
        if "requires_research" in result:
            print(f"Requires Research: {result.get('requires_research')}")
        print("-" * 20 + "\n")
    except Exception as e:
        import traceback
        print(f"\n❌ Error during test: {e}")
        traceback.print_exc()

async def main():
    # Test L1: Casual Greeting
    await test_query("Layer 1 (Casual)", "Namaste Nani, how are you today?")

    # Test L2: Simple Clinical (Data from DB needed)
    await test_query("Layer 2 (Simple Clinical)", "What are my current allergies?")

    # Test L3: Complex / High-Risk (Reasoning required)
    await test_query("Layer 3 (Complex / Reasoning)", "I'm having sudden sharp pain in my chest, what should I do?")

if __name__ == "__main__":
    asyncio.run(main())

