"""
Test Proactive Monitoring Logic
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

from hierarchical_agent.proactive_monitor import proactive_monitor_node

load_dotenv()

async def test_proactive_monitor_node():
    """Test proactive monitor node with different scenarios"""
    print("\n" + "="*60)
    print("PROACTIVE MONITOR TEST SUITE")
    print("="*60)
    
    test_scenarios = [
        {
            "name": "High Risk - RED Alert",
            "state": {
                "query": "I'm experiencing severe dizziness",
                "lane": "safety_check",
                "final_response": "RED ALERT: Severe dizziness may indicate serious condition...",
                "triage_urgency": "high",
                "diagnosis": "Severe dizziness"
            }
        },
        {
            "name": "Moderate Risk - AMBER Alert",
            "state": {
                "query": "My blood pressure has been elevated",
                "lane": "safety_check",
                "final_response": "AMBER: Elevated blood pressure may require monitoring...",
                "triage_urgency": "moderate",
                "diagnosis": "Hypertension monitoring"
            }
        },
        {
            "name": "Drug Interaction",
            "state": {
                "query": "I'm taking metformin and ibuprofen together",
                "lane": "fast_track",
                "final_response": "There may be an interaction between metformin and ibuprofen...",
                "triage_urgency": "moderate",
                "diagnosis": "Potential drug interaction"
            }
        },
        {
            "name": "Pain Symptom",
            "state": {
                "query": "I have pain in my abdomen",
                "lane": "fast_track",
                "final_response": "Abdominal pain could indicate various conditions...",
                "triage_urgency": "moderate",
                "diagnosis": "Abdominal pain"
            }
        },
        {
            "name": "Low Risk - General Question",
            "state": {
                "query": "What are the benefits of exercise?",
                "lane": "fast_track",
                "final_response": "Exercise has many health benefits...",
                "triage_urgency": "none",
                "diagnosis": None
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {scenario['name']} ---")
        print(f"Query: {scenario['state']['query']}")
        
        result = await proactive_monitor_node(scenario['state'])
        
        follow_up = result.get('follow_up_needed', False)
        reason = result.get('follow_up_reason', 'N/A')
        time = result.get('follow_up_time', 'N/A')
        
        print(f"Follow-up Needed: {follow_up}")
        print(f"Reason: {reason[:100] if reason else 'None'}...")
        print(f"Time: {time}")
        
        # Verify expected behavior
        if 'Emergency' in scenario['name']:
            assert not follow_up, "Emergency should not trigger follow-up"
        elif 'High Risk' in scenario['name']:
            assert follow_up, "High risk should trigger follow-up"
        elif 'Moderate Risk' in scenario['name']:
            assert follow_up, "Moderate risk should trigger follow-up"
        elif 'Low Risk' in scenario['name']:
            assert not follow_up, "Low risk should not trigger follow-up"
        
        print(f"✅ Test {i} passed")
    
    print("\n" + "="*60)
    print("✅ ALL PROACTIVE MONITOR TESTS PASSED")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_proactive_monitor_node())
