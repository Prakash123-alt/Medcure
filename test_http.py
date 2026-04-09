import requests
import json

url = "http://localhost:8000/chat"

def run_test(name, message):
    print(f"\n=================================")
    print(f"TESTING: {name}")
    print(f"MESSAGE: '{message}'")
    print(f"=================================")
    
    payload = {
        "message": message,
        "patient_id": "test-user-001"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        print("\n--- RESULTS ---")
        print(f"Triage Level: {data.get('triage_level')}")
        print(f"Triage Reason: {data.get('triage_reason')}")
        print(f"Final Reply:\n{data.get('final_message')}")
        print(f"Errors: {data.get('errors')}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    run_test("Layer 1 (Casual)", "Namaste Nani, how are you today?")
    run_test("Layer 2 (Simple Clinical / Cache Hit)", "What are my allergies?")
    run_test("Layer 3 (Complex / DeepSeek)", "I feel a sharp stinging pain in my lower stomach after eating.")
