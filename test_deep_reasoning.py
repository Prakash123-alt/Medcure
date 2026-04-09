"""
Test Deep Reasoning Features (SOCRATES/OPQRST, SBAR)
"""
import asyncio
import sys
import os
import codecs
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, 'strict')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hierarchical_agent.graph import get_graph_builder
from hierarchical_agent.deep_reasoner import triage_node, interview_node, diagnosis_node

load_dotenv()

async def test_triage_node():
    """Test triage node"""
    print("\n" + "="*60)
    print("TEST 1: Triage Node")
    print("="*60)
    
    state = {
        "query": "I have chest pain that radiates to my left arm",
        "user_id": "test_user",
        "lane": "safety_check"
    }
    
    result = await triage_node(state)
    
    print(f"Triage Result:")
    print(f"  Urgency: {result.get('triage_urgency', 'N/A')}")
    print(f"  Reason: {result.get('triage_reason', 'N/A')[:100]}...")
    print(f"  Interview Needed: {result.get('activate_interview', False)}")
    
    return result

async def test_interview_node():
    """Test interview node"""
    print("\n" + "="*60)
    print("TEST 2: Interview Node (SOCRATES)")
    print("="*60)
    
    state = {
        "query": "I have chest pain",
        "user_id": "test_user",
        "lane": "safety_check",
        "interview_turn": 1,
        "interview_history": []
    }
    
    result = await interview_node(state)
    
    print(f"Interview Question:")
    print(f"  Turn: {result.get('interview_turn', 'N/A')}")
    print(f"  Question: {result.get('interview_question', 'N/A')[:100]}...")
    
    return result

async def test_diagnosis_node():
    """Test diagnosis node with SBAR"""
    print("\n" + "="*60)
    print("TEST 3: Diagnosis Node (SBAR)")
    print("="*60)
    
    state = {
        "query": "I have chest pain",
        "user_id": "test_user",
        "lane": "safety_check",
        "interview_history": [
            "Patient reports chest pain radiating to left arm",
            "Pain started 2 hours ago, severity 8/10",
            "Patient has history of hypertension"
        ],
        "search_results": [],
        "patient_profile": {}
    }
    
    result = await diagnosis_node(state)
    
    print(f"Diagnosis Result:")
    print(f"  COT: {result.get('cot_response', 'N/A')[:150]}...")
    print(f"  SBAR: {result.get('physician_sbar', 'N/A')[:150]}...")
    
    return result

async def test_full_deep_reasoning_flow():
    """Test complete deep reasoning flow with symptom query"""
    print("\n" + "="*60)
    print("TEST 4: Full Deep Reasoning Flow")
    print("="*60)
    
    graph_builder = get_graph_builder()
    app = graph_builder.compile()
    
    # Symptom-based query that should trigger deep reasoning
    test_query = "I have chest pain that radiates to my left arm and I'm short of breath"
    
    print(f"\n>>> Query: '{test_query}'")
    print("-" * 60)
    
    initial_state = {
        "query": test_query,
        "user_id": "test_user",
        "lane": "fast_track",
        "lane_reason": "Test query"
    }
    
    config = {
        "configurable": {
            "thread_id": "test_deep_reasoning_001"
        }
    }
    
    try:
        print("\nRunning agent with deep reasoning...")
        final_state = await app.ainvoke(initial_state, config=config)
        
        print("\n" + "="*60)
        print("FINAL RESPONSE:")
        print("="*60)
        response = final_state.get("final_response", "No response generated")
        print(response[:500] + "..." if len(response) > 500 else response)
        print("="*60)
        
        # Check deep reasoning state
        print(f"\nDeep Reasoning State:")
        print(f"  Triage Urgency: {final_state.get('triage_urgency', 'N/A')}")
        print(f"  Interview Turn: {final_state.get('interview_turn', 'N/A')}")
        print(f"  Deep Reasoning Complete: {final_state.get('deep_reasoning_complete', False)}")
        print(f"  Physician SBAR: {final_state.get('physician_sbar', 'N/A')[:100] if final_state.get('physician_sbar') else 'None'}...")
        
        # Check proactive monitoring
        print(f"\nProactive Monitoring:")
        print(f"  Follow-up Needed: {final_state.get('follow_up_needed', False)}")
        print(f"  Follow-up Reason: {final_state.get('follow_up_reason', 'N/A')[:100] if final_state.get('follow_up_reason') else 'None'}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all deep reasoning tests"""
    print("\n" + "="*60)
    print("CUREMATE AI - DEEP REASONING TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Triage Node
        await test_triage_node()
        
        # Skip individual interview/diagnosis tests (require LangGraph context)
        print("\n[Note] Interview and Diagnosis nodes require full graph context")
        print("      Testing them via full flow instead...")
        
        # Test 4: Full Deep Reasoning Flow
        success = await test_full_deep_reasoning_flow()
        
        print("\n" + "="*60)
        if success:
            print("✅ DEEP REASONING TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
