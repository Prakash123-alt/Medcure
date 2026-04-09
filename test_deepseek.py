import os
from dotenv import load_dotenv
load_dotenv()

from medical_ai_agent.graph import build_graph

graph = build_graph()

def test_deepseek_query():
    print(f"\n==================================================")
    print(f"TESTING: Layer 3 (DeepSeek Reasoning - Non Emergency)")
    message = "I have been experiencing mild fatigue lately. Are there known interactions between taking Atorvastatin and drinking Grapefruit juice every morning?"
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
    
    print("\n--- GRAPH EXECUTION STARTED ---")
    try:
        # Stream the graph execution to clearly see the nodes being hit
        for event in graph.stream(initial_state):
            for node_name, node_state in event.items():
                print(f"[{node_name.upper()} COMPLETED]")
        
        # Get the final state from the stream
        print("\n--- FINAL RESULTS ---")
        if node_state:
            print(f"Final Message:\n{node_state.get('final_message')}")
            print(f"Errors (if any): {node_state.get('errors')}")
        
    except Exception as e:
        import traceback
        print(f"\n❌ Error during test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_deepseek_query()
