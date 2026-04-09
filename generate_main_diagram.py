import base64
import urllib.request
import urllib.parse
from PIL import Image
import io

def create_main_architecture_jpeg():
    mermaid_code = """flowchart TD
    WA[("📱 WhatsApp\\nUser Message")] --> TWILIO["Twilio Webhook\\nPOST /webhook/whatsapp"]
    TWILIO --> API["FastAPI\\napi.py"]

    API --> ONBOARD{"Is user\\nonboarded?"}
    ONBOARD -- "No → collect\\nName/Age/Gender" --> DB_WRITE[("🗄️ Cloud SQL\\nPostgreSQL")]
    ONBOARD -- "Yes" --> ROUTE_INPUT

    ROUTE_INPUT{"Input\\nType?"} --> |"🖼️ Prescription\\nImage"| OCR
    ROUTE_INPUT --> |"🍎 Food\\nImage"| NUTRI
    ROUTE_INPUT --> |"💬 Text\\nMessage"| TRIAGE

    %% ── OCR PIPELINE ──
    OCR["🔍 OCR Extraction\\nGemini 2.5 Flash\\n+ Logprobs Confidence"]
    OCR --> VERIFY["✅ Verification Loop\\nFuzzy Match vs DB\\n+ Serper API lookup"]
    VERIFY --> CTX

    %% ── NUTRITIONIST ──
    NUTRI["🥗 Food Vision Node\\nGemini Vision\\nNutritional Analysis"] --> PERSONA

    %% ── SMART SINGLE-CALL TRIAGE ──
    TRIAGE["🧠 Smart Triage\\n(triage_and_respond_node)\\nGemini 2.5 Flash"] --> TRIAGE_ROUTE

    TRIAGE_ROUTE{"Triage\\nLevel?"}
    
    %% L1 — SINGLE CALL END-TO-END
    TRIAGE_ROUTE -- "L1 Casual/Factual\\n(~2s)" --> FAST_RESPOND["⚡ Fast Response\\nGenerated directly in Triage!"]
    FAST_RESPOND --> TTS_ASYNC["🔊 TTS Engine\\n(Background Thread)"]
    TTS_ASYNC --> SEND

    %% L2 — DB ONLY
    TRIAGE_ROUTE -- "L2 Simple Clinical\\n(~5s)" --> CTX_FAST["⚡ Fast Context\\nDB Snapshot Only\\n(No RAG)"]
    CTX_FAST --> PERSONA

    %% L3 — FULL PIPELINE
    TRIAGE_ROUTE -- "L3 Complex\\n(~15s)" --> CTX["📋 Context Retrieval\\nPatient Snapshot\\n+ Long-Term Memory"]
    CTX --> RAG["📚 AIIMS RAG\\npgvector Cosine Search"]
    
    RAG --> REASON["🤖 Gemini 2.5 Flash Thinking\\nNative Tool Calling\\nClinical Reasoning"]
    
    REASON --> REASON_ROUTE{"Needs\\nSearch?"}
    REASON_ROUTE -- "Yes" --> RESEARCH["🔎 Researcher Node\\nGoogle Search Tool"]
    RESEARCH --> REASON
    
    REASON_ROUTE -- "No" --> PERSONA

    %% ── OUTPUT ──
    PERSONA["🎭 Persona Node\\nSister Nani\\nInline Anti-Hallucination"]
    PERSONA --> TTS_ASYNC
    
    %% ── EMERGENCY ──
    TRIAGE_ROUTE -- "🚨 Emergency" --> HITL["🚑 Human In The Loop\\nEmergency Escalation"]

    %% ── MEMORY ──
    SEND["📤 Twilio Send\\nText + Voice\\nto WhatsApp"] --> MEM["🧠 Memory Manager\\n(Background Thread)"]
    MEM --> DB_WRITE

    %% ── STYLING ──
    classDef input fill:#1a1a2e,stroke:#00d4ff,color:#fff
    classDef fast fill:#0f3460,stroke:#00ff88,color:#fff
    classDef l3 fill:#16213e,stroke:#7c4dff,color:#fff
    classDef output fill:#0d2137,stroke:#ff6b35,color:#fff
    classDef db fill:#1a1a1a,stroke:#ffd700,color:#fff
    classDef danger fill:#3d0000,stroke:#ff0000,color:#fff

    class WA,TWILIO,API input
    class TRIAGE,CTX_FAST,NUTRI,FAST_RESPOND,TTS_ASYNC fast
    class CTX,RAG,REASON,RESEARCH l3
    class PERSONA,SEND output
    class DB_WRITE,MEM db
    class HITL danger
"""

    graphbytes = mermaid_code.encode("utf-8")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("utf-8")

    url = f"https://mermaid.ink/img/{base64_string}?bgColor=white"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image_data = response.read()

        img = Image.open(io.BytesIO(image_data))
        rgb_img = img.convert('RGB')
        output_file = "main_architecture.jpeg"
        rgb_img.save(output_file, "JPEG")
        
        print(f"Successfully generated and saved as {output_file}")
    except Exception as e:
        print(f"Failed to generate diagram: {e}")

if __name__ == "__main__":
    create_main_architecture_jpeg()
