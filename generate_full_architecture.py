import base64
import urllib.request
from PIL import Image
import io

def generate_full_architecture_jpeg():
    mermaid_code = """flowchart TD
    %% Base Setup
    classDef start_end fill:#1a1a2e,stroke:#00d4ff,color:#fff,stroke-width:2px
    classDef router fill:#0d2137,stroke:#ff6b35,color:#fff,rx:5px,ry:5px
    classDef data fill:#0f3460,stroke:#00ff88,color:#fff
    classDef reasoning fill:#16213e,stroke:#7c4dff,color:#fff
    classDef danger fill:#3d0000,stroke:#ff0000,color:#fff,rx:10px
    classDef safety fill:#311b92,stroke:#b388ff,color:#fff
    classDef user fill:#2d3436,stroke:#74b9ff,color:#fff

    USER(("👤 User (WhatsApp/Web)")):::user

    START((("__start__"))):::start_end
    END_NODE((("__end__"))):::start_end
    
    USER <-->|WebSocket/Twilio| START

    %% Phase 1: Ingestion & Optimization
    START --> HISTORY_CHECK{"History > Max?"}:::router
    HISTORY_CHECK -- "Yes" --> SUMMARIZER["Summarizer Node<br/>(Context Compression)"]:::data
    HISTORY_CHECK -- "No" --> SMART_ROUTER
    SUMMARIZER --> SMART_ROUTER["Smart Router<br/>(Input Classification)"]:::router

    %% Input Routing
    SMART_ROUTER -- "Medicine Photo" --> OCR["OCR Extraction<br/>(Gemini Vision)"]:::data
    SMART_ROUTER -- "Food Photo" --> NUTRI["Nutritionist<br/>(Diet Vision)"]:::reasoning
    SMART_ROUTER -- "Vitals Text" --> VITALS["Vitals Parser<br/>(Regex/Logic)"]:::data
    SMART_ROUTER -- "Clinical/Casual Text" --> TRIAGE["Triage Node<br/>(L1/L2/L3)"]:::router
    SMART_ROUTER -- "Blocked by Guardrail" --> END_NODE

    %% Specialized Linear Pipelines
    OCR --> VERIFY["Verification Loop<br/>(1mg DB + Serper)"]:::data --> END_NODE
    NUTRI --> PERSONA_SYNTHESIS
    VITALS -- "Critical" --> HITL["Human In The Loop<br/>(Escalation)"]:::danger
    VITALS -- "Normal" --> TRIAGE

    %% Triage Sub-Routing
    TRIAGE --> TRIAGE_LEVEL{"Severity<br/>Level?"}:::router
    TRIAGE_LEVEL -- "Emergency" --> HITL
    TRIAGE_LEVEL -- "Clarification needed" --> SYMPTOM["Symptom Clarifier<br/>Interview"]:::data --> END_NODE
    TRIAGE_LEVEL -- "L1 (Casual)" --> PERSONA["L1 Persona Node<br/>(Fast Greeting)"]:::data
    TRIAGE_LEVEL -- "L2 (Basic Clinical)" --> CTX_FAST["Context Retrieval<br/>(Fast)"]:::data
    TRIAGE_LEVEL -- "L3 (Complex)" --> PROVISIONAL["Provisional Responder<br/>(Zero-Wait Hold Msg)"]:::data
    
    PROVISIONAL --> CTX["Context Retrieval<br/>(History + Vitals)"]:::reasoning

    %% L1 Fast Path
    PERSONA --> PERSONA_CHECK{"Clinical Content?"}:::router
    PERSONA_CHECK -- "No" --> MEMORY_WRITER
    PERSONA_CHECK -- "Yes" --> GRADER

    %% Phase 2: Core Clinical Brain (L2/L3)
    CTX_FAST --> PERSONA_SYNTHESIS
    CTX --> DDI["DDI Checker<br/>(Drug Interactions)"]:::reasoning
    DDI --> RAG["AIIMS Guidelines RAG<br/>(pgvector)"]:::reasoning
    RAG --> DDX["Differential Diagnosis"]:::reasoning
    DDX --> SEARCH_DECISION{"Requires Web<br/>Research?"}:::router
    
    SEARCH_DECISION -- "Yes" --> RESEARCHER["Researcher<br/>(DuckDuckGo/Search)"]:::data --> SEARCH_DECISION
    SEARCH_DECISION -- "No (L2)" --> L2_REASON["L2 Reasoning<br/>(Gemini Flash)"]:::reasoning
    SEARCH_DECISION -- "No (L3)" --> RAT_REASON["RAT Deep Reasoning<br/>(DeepSeek R1)"]:::reasoning

    %% Reasoning Outcomes
    L2_REASON --> L2_OUTCOME{"Outcome?"}:::router
    L2_OUTCOME -- "Escalate to L3" --> CTX
    L2_OUTCOME -- "Safety Issue" --> HITL
    L2_OUTCOME -- "Cleared" --> PERSONA_SYNTHESIS["Persona Synthesizer<br/>('Sister Nani' Voice)"]:::data

    RAT_REASON --> RAT_OUTCOME{"Confidence < Threshold?"}:::router
    RAT_OUTCOME -- "Yes" --> HITL
    RAT_OUTCOME -- "No" --> PERSONA_SYNTHESIS

    %% Safety & Verification
    PERSONA_SYNTHESIS --> FINAL_QA{"Clarification<br/>Response?"}:::router
    FINAL_QA -- "Yes" --> END_NODE
    FINAL_QA -- "No" --> GRADER["Guardrail Grader<br/>(Hallucination Check)"]:::safety

    %% Guardrail Loop
    GRADER --> GRADER_OUTCOME{"Grade?"}:::router
    GRADER_OUTCOME -- "FAIL_HIGH" --> RAT_REASON
    GRADER_OUTCOME -- "PASS / CORRECTED" --> GRADER_L3_CHECK{"Was it L3?"}:::router

    GRADER_L3_CHECK -- "Yes" --> CITATION["Citation Grader"]:::safety --> MEMORY_WRITER
    GRADER_L3_CHECK -- "No" --> MEMORY_WRITER["Memory Writer<br/>(Semantic DB Commit)"]:::data

    MEMORY_WRITER --> END_NODE
    HITL --> END_NODE
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
        output_file = "full_architecture_analysis.jpeg"
        rgb_img.save(output_file, "JPEG")
        
        print(f"Successfully generated and saved as {output_file}")
    except Exception as e:
        print(f"Failed to generate diagram: {e}")
        # print the base64 URL for debugging
        print(f"URL: {url}")

if __name__ == "__main__":
    generate_full_architecture_jpeg()
