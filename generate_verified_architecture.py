import base64
import urllib.request
from PIL import Image
import io

def generate_verified_architecture_jpeg():
    # This mermaid graph accurately reflects the workflow definition in graph.py (lines 380-510)
    mermaid_code = """flowchart TD
    %% Base Setup
    classDef start_end fill:#1a1a2e,stroke:#00d4ff,color:#fff,stroke-width:2px
    classDef router fill:#0d2137,stroke:#ff6b35,color:#fff,rx:5px,ry:5px
    classDef data fill:#0f3460,stroke:#00ff88,color:#fff
    classDef reasoning fill:#16213e,stroke:#7c4dff,color:#fff
    classDef danger fill:#3d0000,stroke:#ff0000,color:#fff,rx:10px
    classDef safety fill:#311b92,stroke:#b388ff,color:#fff

    START((("__start__"))):::start_end
    END_NODE((("__end__"))):::start_end
    
    %% Phase 1: Ingestion & Optimization
    START --> ROUTE_FROM_START{"History > Max?"}:::router
    ROUTE_FROM_START -- "summarizer" --> SUMMARIZER["Summarizer Node"]:::data
    ROUTE_FROM_START -- "smart_router" --> SMART_ROUTER["Smart Router"]:::router
    SUMMARIZER --> SMART_ROUTER

    %% Input Routing
    SMART_ROUTER -- "ocr_extraction" --> OCR["OCR Extraction"]:::data
    SMART_ROUTER -- "nutritionist" --> NUTRI["Nutritionist"]:::reasoning
    SMART_ROUTER -- "vitals_parser" --> VITALS["Vitals Parser"]:::data
    SMART_ROUTER -- "triage" --> TRIAGE["Triage Node"]:::router
    SMART_ROUTER -- "context_retrieval" --> CTX["Context Retrieval"]:::reasoning
    SMART_ROUTER -- "END (Blocked)" --> END_NODE

    %% Vitals & OCR
    VITALS -- "triage" --> TRIAGE
    VITALS -- "human_in_the_loop" --> HITL["Human In The Loop"]:::danger
    OCR --> VERIFY["Verification Loop"]:::data --> END_NODE
    NUTRI --> PERSONA_SYNTHESIS["Persona Synthesizer"]:::data

    %% Triage Sub-Routing
    TRIAGE -- "persona" --> PERSONA["L1 Persona Node"]:::data
    TRIAGE -- "context_retrieval_fast" --> CTX_FAST["Fast Context Retrieval"]:::data
    TRIAGE -- "context_retrieval" --> CTX
    TRIAGE -- "provisional_responder" --> PROVISIONAL["Provisional Responder"]:::data
    TRIAGE -- "symptom_clarifier" --> SYMPTOM["Symptom Clarifier"]:::data
    TRIAGE -- "human_in_the_loop" --> HITL

    SYMPTOM --> END_NODE
    CTX_FAST --> PERSONA_SYNTHESIS
    PROVISIONAL --> CTX

    %% Core Clinical Reasoning
    CTX --> DDI["DDI Checker"]:::reasoning
    DDI --> RAG["AIIMS Guidelines RAG"]:::reasoning
    RAG --> DDX["Differential Diagnosis"]:::reasoning
    DDX --> SEARCH_DECISION{"Requires Web Research?"}:::router
    
    SEARCH_DECISION -- "researcher" --> RESEARCHER["Researcher"]:::data --> SEARCH_DECISION
    SEARCH_DECISION -- "l2_reasoning" --> L2["L2 Reasoning"]:::reasoning
    SEARCH_DECISION -- "rat_reasoning" --> RAT["RAT Deep Reasoning"]:::reasoning

    %% L2 & RAT Outcomes
    L2 -- "persona_synthesizer" --> PERSONA_SYNTHESIS
    L2 -- "context_retrieval (Escalate)" --> CTX
    L2 -- "human_in_the_loop" --> HITL

    RAT -- "persona_synthesizer" --> PERSONA_SYNTHESIS
    RAT -- "human_in_the_loop" --> HITL

    %% Guardrail Loop
    PERSONA -- "guardrail_grader" --> GRADER["Guardrail Grader"]:::safety
    PERSONA -- "memory_writer" --> MEMORY_WRITER["Memory Writer"]:::data
    PERSONA -- "END" --> END_NODE
    
    PERSONA_SYNTHESIS -- "guardrail_grader" --> GRADER
    PERSONA_SYNTHESIS -- "END" --> END_NODE

    GRADER -- "rat_reasoning (FAIL_HIGH)" --> RAT
    GRADER -- "memory_writer (PASS/CORRECTED)" --> MEMORY_WRITER
    GRADER -- "citation_grader (L3)" --> CITATION["Citation Grader"]:::safety

    CITATION --> MEMORY_WRITER
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
        output_file = "verified_architecture.jpeg"
        rgb_img.save(output_file, "JPEG")
        
        print(f"Successfully generated and saved as {output_file}")
    except Exception as e:
        print(f"Failed to generate diagram: {e}")
        print(f"URL: {url}")

if __name__ == "__main__":
    generate_verified_architecture_jpeg()
