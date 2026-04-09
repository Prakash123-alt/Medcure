import base64
import urllib.request
from PIL import Image
import io

def create_updated_architecture_jpeg():
    mermaid_code = """flowchart TD
    START((User Input)) --> SUMM["Summarizer Node<br/>(Context Optimization)"]
    
    %% Input Routing
    SUMM --> ROUTE_START{"Input<br/>Type?"}
    ROUTE_START -- "Prescription" --> OCR["OCR Extraction"]
    ROUTE_START -- "Food Image" --> NUTRI["Nutritionist<br/>(Food Vision)"]
    ROUTE_START -- "Active Follow-Up" --> CTX["Context Retrieval"]
    ROUTE_START -- "Text/Audio" --> TRIAGE["Smart Triage"]
    
    %% OCR Pipeline
    OCR --> VERIFY["Verification Loop<br/>(DB + Serper)"]
    VERIFY --> END_OCR((END))
    
    %% Triage Routing
    TRIAGE --> TRIAGE_ROUTE{"Triage<br/>Level / Flag?"}
    TRIAGE_ROUTE -- "Emergency" --> HITL["Human In The Loop<br/>(Escalation)"]
    TRIAGE_ROUTE -- "Clarification" --> SYMPTOM["Symptom Clarifier<br/>Interview"]
    TRIAGE_ROUTE -- "L1 (Casual)" --> PERSONA["Persona Node"]
    TRIAGE_ROUTE -- "L2 (Mid) / L3 (Complex)" --> CTX
    
    SYMPTOM --> END_SYMPTOM((END))
    HITL --> END_HITL((END))
    
    %% Clinical Brain Pipeline
    CTX --> DDI["DDI Checker<br/>(Drug Interactions)"]
    DDI --> RAG["AIIMS RAG<br/>(Graph + Vector)"]
    RAG --> SEARCH_DEC{"Needs<br/>Search?"}
    
    SEARCH_DEC -- "Yes" --> RESEARCHER["Researcher<br/>(Google Search)"]
    RESEARCHER --> SEARCH_DEC
    
    SEARCH_DEC -- "No (L2)" --> L2_REASON["L2 Reasoning"]
    SEARCH_DEC -- "No (L3)" --> L3_REASON["Deep Reasoning"]
    
    L2_REASON --> L2_ESCALATE{"Escalate<br/>to L3?"}
    L2_ESCALATE -- "Yes" --> CTX
    L2_ESCALATE -- "No" --> PERSONA
    
    L3_REASON --> PERSONA
    NUTRI --> PERSONA
    
    %% Output Safety
    PERSONA --> CLARIFY_CHECK{"Asking for<br/>Clarification?"}
    CLARIFY_CHECK -- "Yes (Skip Grader)" --> END_FAST((END))
    CLARIFY_CHECK -- "No" --> GRADER["Guardrail Grader"]
    
    GRADER --> END_FINAL((END))
    
    %% Styling
    classDef start fill:#1a1a2e,stroke:#00d4ff,color:#fff
    classDef router fill:#0d2137,stroke:#ff6b35,color:#fff
    classDef fast fill:#0f3460,stroke:#00ff88,color:#fff
    classDef l3 fill:#16213e,stroke:#7c4dff,color:#fff
    classDef danger fill:#3d0000,stroke:#ff0000,color:#fff
    classDef safety fill:#311b92,stroke:#b388ff,color:#fff
    
    class START,SUMM start
    class ROUTE_START,TRIAGE_ROUTE,SEARCH_DEC,L2_ESCALATE,CLARIFY_CHECK router
    class OCR,VERIFY,NUTRI,TRIAGE,PERSONA,SYMPTOM fast
    class CTX,DDI,RAG,RESEARCHER,L2_REASON,L3_REASON l3
    class HITL danger
    class GRADER safety
"""

    graphbytes = mermaid_code.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("utf-8")

    url = f"https://mermaid.ink/img/{base64_string}?bgColor=white"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()

        img = Image.open(io.BytesIO(image_data))
        rgb_img = img.convert('RGB')
        output_file = "updated_architecture.jpeg"
        rgb_img.save(output_file, "JPEG")
        
        print(f"Successfully generated and saved as {output_file}")
    except Exception as e:
        print(f"Failed to generate diagram: {e}")
        # print the base64 URL for debugging
        print(f"URL: {url}")

if __name__ == "__main__":
    create_updated_architecture_jpeg()
