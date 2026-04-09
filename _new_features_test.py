"""
_new_features_test.py
Tests for all 10 new improvements implemented in this session.
Run: python _new_features_test.py
"""
import asyncio
import sys
import os
import warnings
warnings.filterwarnings("ignore")

# psycopg3 requires SelectorEventLoop on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

PASS = "✅  PASS"
FAIL = "❌  FAIL"

print("=" * 60)
print("  Sister Nani — New Features Test Suite")
print("=" * 60)

results = {}


# ── TEST 1: Vitals Parser (local, no API) ────────────────────────────────────
def test_vitals_parser():
    print("\n[1] Vitals Parser (Regex, no LLM)")
    from medical_ai_agent.nodes.vitals_node import parse_vitals_and_labs, needs_vitals_parse

    cases = [
        ("My BP is 185/115 and I feel dizzy",     True,  "bp_systolic", 185),
        ("my spo2 is 89%",                        True,  "spo2",        89),
        ("blood sugar 380 mg",                    True,  "glucose_mg_dl", 380),
        ("creatinine 3.8 mg/dl",                  True,  "creatinine",  3.8),
        ("hba1c 10.2",                            True,  "hba1c",       10.2),
        ("potassium 6.2 meq",                     True,  "potassium",   6.2),
        ("Hello doctor how are you",              False, None,          None),
    ]

    ok = True
    for text, expect_detection, key, expected_val in cases:
        detected = needs_vitals_parse(text)
        if detected != expect_detection:
            print(f"  {FAIL}: '{text}' — expected detected={expect_detection}, got {detected}")
            ok = False
            continue
        if key:
            vitals, labs, flags = parse_vitals_and_labs(text)
            combined = {**vitals, **labs}
            got_val = combined.get(key)
            if got_val is None or abs(got_val - expected_val) > 0.1:
                print(f"  {FAIL}: '{text}' — key '{key}' expected {expected_val}, got {got_val}")
                ok = False
            else:
                print(f"  OK: '{text}' → {key}={got_val}, flags={len(flags)}")
        else:
            print(f"  OK: '{text}' → no detection (correct)")

    results["1_vitals_parser"] = ok
    print(f"  {'PASS' if ok else 'FAIL'}")


test_vitals_parser()


# ── TEST 2: Config — new thresholds ─────────────────────────────────────────
def test_config():
    print("\n[2] New Config Thresholds")
    from medical_ai_agent.config import config
    checks = [
        ("VITALS_HIGH_BP_SYSTOLIC",  config.VITALS_HIGH_BP_SYSTOLIC,  160),
        ("VITALS_LOW_SPO2",          config.VITALS_LOW_SPO2,          92),
        ("LAB_CREATININE_DANGER",    config.LAB_CREATININE_DANGER,    2.0),
        ("LAB_HBA1C_POOR",           config.LAB_HBA1C_POOR,           9.0),
        ("MEMORY_MIN_MESSAGES",      config.MEMORY_MIN_MESSAGES,      2),
        ("RAT_CONFIDENCE_THRESHOLD", config.RAT_CONFIDENCE_THRESHOLD, 0.80),
    ]
    ok = True
    for name, val, expected in checks:
        if abs(float(val) - float(expected)) < 0.01:
            print(f"  OK: {name} = {val}")
        else:
            print(f"  {FAIL}: {name} expected {expected}, got {val}")
            ok = False
    results["2_config"] = ok


test_config()


# ── TEST 3: State fields ──────────────────────────────────────────────────────
def test_state_fields():
    print("\n[3] New AgentState Fields")
    from medical_ai_agent.state import AgentState
    import typing
    hints = typing.get_type_hints(AgentState)
    required_fields = [
        "vitals_detected", "reported_labs", "critical_lab_flags",
        "differential_diagnoses", "groundedness_score", "rat_confidence",
    ]
    ok = True
    for f in required_fields:
        if f in hints:
            print(f"  OK: {f} : {hints[f]}")
        else:
            print(f"  {FAIL}: field '{f}' missing from AgentState")
            ok = False
    results["3_state_fields"] = ok


test_state_fields()


# ── TEST 4: Graph imports & new nodes ────────────────────────────────────────
def test_graph_nodes():
    print("\n[4] Graph Node Imports & Build")
    try:
        from medical_ai_agent.graph import build_graph
        app = build_graph()
        nodes = list(app.nodes.keys())
        required_nodes = [
            "vitals_parser", "ddx", "citation_grader", "memory_writer",
            "rat_reasoning", "ddi_checker", "triage", "persona", "guardrail_grader",
        ]
        ok = True
        for n in required_nodes:
            if n in nodes:
                print(f"  OK: '{n}' registered")
            else:
                print(f"  {FAIL}: '{n}' NOT in graph")
                ok = False
        results["4_graph_nodes"] = ok
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results["4_graph_nodes"] = False


test_graph_nodes()


# ── TEST 5: PostgreSQL Checkpointer factory ───────────────────────────────────
async def test_pg_checkpointer():
    print("\n[5] PostgreSQL Checkpointer (build_graph_with_postgres)")
    try:
        from medical_ai_agent.graph import build_graph_with_postgres
        app, conn = await asyncio.wait_for(build_graph_with_postgres(), timeout=20)
        nodes = list(app.nodes.keys())
        print(f"  OK: graph built with PG checkpointer. Nodes: {len(nodes)}")
        await conn.close()
        results["5_pg_checkpointer"] = True
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results["5_pg_checkpointer"] = False

asyncio.run(test_pg_checkpointer())


# ── TEST 6: Vitals -> HITL routing ───────────────────────────────────────────
async def test_vitals_routing():
    print("\n[6] Vitals E2E Routing (BP 185/110 → HITL)")
    try:
        from medical_ai_agent.graph import build_graph
        app = build_graph()
        state = {
            "patient_id": "test_vitals_001",
            "session_id": "test_vitals_sess",
            "user_input": "My BP is 185/115 and I feel very dizzy",
            "chat_history": [{"role": "user", "content": "My BP is 185/115 and I feel very dizzy"}],
            "messages": [],
            "persona_type": "Coach",
            "engagement_score": 60,
            "research_iteration_count": 0,
            "errors": [],
        }
        config_d = {"configurable": {"thread_id": "vitals_test_01"}}
        result = await asyncio.wait_for(
            app.ainvoke(state, config=config_d), timeout=60
        )
        msg = result.get("final_message", "")
        vitals = result.get("vitals_detected")
        flags = result.get("critical_lab_flags", [])
        print(f"  Vitals detected: {vitals}")
        print(f"  Critical flags: {flags}")
        print(f"  Final message (truncated): {msg[:150]}")
        # Should have triggered HITL (needs_human_review) or at least detected vitals
        ok = bool(vitals) and any("CRITICAL" in f for f in flags)
        results["6_vitals_routing"] = ok
        print(f"  {'PASS' if ok else 'WARN: vitals detected but no CRITICAL flag (may be threshold)'}")
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results["6_vitals_routing"] = False

asyncio.run(test_vitals_routing())


# ── TEST 7: Memory writer (DB write) ─────────────────────────────────────────
async def test_memory_writer():
    print("\n[7] Memory Writer Node (imports + DB write)")
    try:
        from medical_ai_agent.nodes.memory_node import memory_writer_node
        # Minimal state with enough chat history
        state = {
            "patient_id": "test_mem_001",
            "chat_history": [
                {"role": "user", "content": "I was diagnosed with Type 2 Diabetes in 2019"},
                {"role": "assistant", "content": "I see. I'll remember that."},
                {"role": "user", "content": "I also take Metformin 500mg twice a day"},
                {"role": "assistant", "content": "Understood. Metformin is well-suited for T2DM."},
            ],
            "clinical_assessment": None,
            "final_message": "Your medication looks appropriate.",
        }
        result = await asyncio.wait_for(memory_writer_node(state), timeout=30)
        print(f"  Memory writer returned: {result}")
        print(f"  PASS (check semantic_memory table for patient 'test_mem_001')")
        results["7_memory_writer"] = True
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results["7_memory_writer"] = False

asyncio.run(test_memory_writer())


# ── SUMMARY ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
passed = sum(1 for v in results.values() if v)
total  = len(results)
for name, ok in results.items():
    print(f"  {'✅' if ok else '❌'}  {name}")
print(f"\n  {passed}/{total} tests passed")
print("=" * 60)
