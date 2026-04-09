# Sister Nani — Full Architecture Diagrams

## Current Architecture (v2 — Deployed)

```mermaid
flowchart TD
    WA[("📱 WhatsApp\nUser Message")] --> TWILIO["Twilio Webhook\nPOST /webhook/whatsapp"]
    TWILIO --> API["FastAPI\napi.py"]

    API --> ONBOARD{"Is user\nonboarded?"}
    ONBOARD -- "No → collect\nName/Age/Gender" --> DB_WRITE[("🗄️ Cloud SQL\nPostgreSQL")]
    ONBOARD -- "Yes" --> ROUTE_INPUT

    ROUTE_INPUT{"Input\nType?"} --> |"🖼️ Prescription\nImage"| OCR
    ROUTE_INPUT --> |"🍎 Food\nImage"| NUTRI
    ROUTE_INPUT --> |"💬 Text\nMessage"| TRIAGE

    %% ── OCR PIPELINE ──
    OCR["🔍 OCR Extraction\nGemini 2.5 Flash\n+ Logprobs Confidence"]
    OCR --> VERIFY["✅ Verification Loop\nFuzzy Match vs DB\n+ Serper API lookup"]
    VERIFY --> CTX

    %% ── NUTRITIONIST ──
    NUTRI["🥗 Food Vision Node\nGemini Vision\nNutritional Analysis"] --> PERSONA

    %% ── SMART SINGLE-CALL TRIAGE ──
    TRIAGE["🧠 Smart Triage\n(triage_and_respond_node)\nGemini 2.5 Flash"] --> TRIAGE_ROUTE

    TRIAGE_ROUTE{"Triage\nLevel?"}
    
    %% L1 — SINGLE CALL END-TO-END
    TRIAGE_ROUTE -- "L1 Casual/Factual\n(~2s)" --> FAST_RESPOND["⚡ Fast Response\nGenerated directly in Triage!"]
    FAST_RESPOND --> TTS_ASYNC["🔊 TTS Engine\n(Background Thread)"]
    TTS_ASYNC --> SEND

    %% L2 — DB ONLY
    TRIAGE_ROUTE -- "L2 Simple Clinical\n(~5s)" --> CTX_FAST["⚡ Fast Context\nDB Snapshot Only\n(No RAG)"]
    CTX_FAST --> PERSONA

    %% L3 — FULL PIPELINE
    TRIAGE_ROUTE -- "L3 Complex\n(~15s)" --> CTX["📋 Context Retrieval\nPatient Snapshot\n+ Long-Term Memory"]
    CTX --> RAG["📚 AIIMS RAG\npgvector Cosine Search"]
    
    RAG --> REASON["🤖 Gemini 2.5 Flash Thinking\nNative Tool Calling\nClinical Reasoning"]
    
    REASON --> REASON_ROUTE{"Needs\nSearch?"}
    REASON_ROUTE -- "Yes" --> RESEARCH["🔎 Researcher Node\nGoogle Search Tool"]
    RESEARCH --> REASON
    
    REASON_ROUTE -- "No" --> PERSONA

    %% ── OUTPUT ──
    PERSONA["🎭 Persona Node\nSister Nani\nInline Anti-Hallucination"]
    PERSONA --> TTS_ASYNC
    
    %% ── EMERGENCY ──
    TRIAGE_ROUTE -- "🚨 Emergency" --> HITL["🚑 Human In The Loop\nEmergency Escalation"]

    %% ── MEMORY ──
    SEND["📤 Twilio Send\nText + Voice\nto WhatsApp"] --> MEM["🧠 Memory Manager\n(Background Thread)"]
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
```

---

## Latency Comparison

```mermaid
xychart-beta
    title "Response Latency: Before vs After"
    x-axis ["L1 (Hi)", "L2 (Allergies?)", "L3 (Chest Pain)"]
    y-axis "Seconds" 0 --> 120
    bar [11, 15, 120]
    bar [2, 5, 18]
```

---

## Node Inventory

| Node | Model Used | Path |
|---|---|---|
| **Triage & Fast Respond** | Gemini 2.5 Flash | L1 Fast Path (All casual/factual queries) |
| **OCR Extraction** | Gemini 2.5 Flash + Logprobs | Prescription images |
| **Verification Loop** | Gemini + Serper + FuzzyMatch | Post-OCR |
| **Food Vision** | Gemini Vision | Food images |
| **Context Retrieval** | PostgreSQL JOIN | L3 full path |
| **AIIMS RAG** | pgvector + VertexAI Embeddings | L3 full path |
| **Reasoning** | Gemini 2.5 Flash Thinking | L3 full path |
| **Researcher** | Google Search Tool (Native) | L3 on demand |
| **Persona/Communicator** | Gemini 2.5 Flash | L2, L3, Nutrition paths |
| **Memory Manager** | Gemini 2.5 Flash + pgvector | Async background |
| **TTS Engine** | Gemini Audio | Async background |
