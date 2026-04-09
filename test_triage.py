from dotenv import load_dotenv
load_dotenv("d:\\project\\AI Agent\\.env")

from medical_ai_agent.nodes.triage import triage_node

state = {
    "user_input": "Hi",
    "chat_history": [],
    "extracted_prescription": None,
    "clinical_assessment": None
}

result = triage_node(state)
print("TRIAGE RESULT:")
print(result)
