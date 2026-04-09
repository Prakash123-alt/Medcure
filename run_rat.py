#!/usr/bin/env python
"""
run_rat.py — Standalone RAT demo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Executes the CureMate RAT engine against the same mock patient data
used by the existing medical_ai_agent pipeline.  **Does not touch any
file inside medical_ai_agent/.**

Usage:
    python run_rat.py                        # mock provider (no API key)
    DEEPSEEK_API_KEY=sk-… python run_rat.py  # live DeepSeek R1

Set RAT_MAX_ITERATIONS and RAT_CONFIDENCE_THRESHOLD in .env or environment.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure the repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

# ── Optional: load .env ─────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from curemate_rat import RATConfig, RATEngine, RATResult
from curemate_rat.retrievers import CallbackRetriever

# ── Sample clinical context (matches the mock data in medical_ai_agent) ─
SAMPLE_CONTEXT = """\
PATIENT HISTORY:
  Patient ID: PT-77291
  Name: Test Patient
  Age: 55, Gender: Male
  Weight: 75.0 kg, Height: 170.0 cm, BMI: 26.0
  Renal Function (CrCl): 103.8 mL/min
  Chronic Conditions: Type 2 Diabetes Mellitus (T2DM), Hypertension (HTN)
  Allergies: Penicillin
  Family History: Father — CAD, Mother — T2DM
  Current Medications: Metformin 500 mg (1-0-1), Amlodipine 5 mg (1-0-0)
  Lab Results:
    - Serum Creatinine: 1.2 mg/dL (normal)
    - HbA1c: 7.8 % (ABNORMAL — target < 5.7 %)

CURRENT PRESCRIPTION:
  Doctor: Dr. Smith  |  Date: 2026-02-20
  Symptoms: Cough, Fever
  Medicines: Asthalin 100 mg (1-0-1, after meals)

DRUG INTERACTIONS:
  (none detected by mock checker)

AIIMS GUIDELINES:
  RAG system unavailable — proceeding with general clinical reasoning.
"""


async def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print("  CureMate RAT — Standalone Demo")
    print("=" * 60)

    # 1. Config
    config = RATConfig.from_env()
    print(f"\nProvider : {config.provider}")
    print(f"Model    : {config.model}")
    print(f"Max iter : {config.max_iterations}")
    print(f"Threshold: {config.confidence_threshold}")

    # 2. Optional retriever (returns a canned guideline for demo)
    async def _demo_search(query: str) -> list[str]:
        return [
            f"[AIIMS Guideline] For query '{query[:60]}…': "
            "Monitor vitals q4h.  Adjust dose per renal function.  "
            "Beta-agonist bronchodilators may raise heart rate — "
            "use with caution in hypertensive patients."
        ]

    retriever = CallbackRetriever(_demo_search, timeout=5.0)

    # 3. Run
    print("\n--- Starting RAT session ---\n")
    engine = RATEngine(config, retriever=retriever)
    result: RATResult = await engine.run(SAMPLE_CONTEXT)

    # 4. Report
    print("\n" + "=" * 60)
    print("  RAT SESSION COMPLETE")
    print("=" * 60)

    print(f"\nProvider       : {result.provider_used}")
    print(f"Iterations     : {result.total_iterations}")
    print(f"Duration       : {result.duration_seconds:.2f}s")
    print(f"Correlation ID : {result.correlation_id}")
    print(f"Confidence     : {result.assessment.confidence:.2f}")

    print(f"\n--- Think Steps ({len(result.think_steps)}) ---")
    for step in result.think_steps:
        print(f"  [{step.iteration}] confidence={step.confidence:.2f}  query={step.retrieval_query or '(none)'}")

    print(f"\n--- Evidence Collected ({len(result.evidence_collected)}) ---")
    for i, ev in enumerate(result.evidence_collected, 1):
        print(f"  [{i}] {ev[:100]}…")

    print("\n--- Final Assessment ---")
    a = result.assessment
    print(f"  Summary       : {a.assessment_summary}")
    print(f"  Risks         : {a.risks_identified}")
    print(f"  Triage        : {a.triage_instructions}")
    print(f"  Red Flags     : {a.red_flags}")
    print(f"  Human Review  : {a.needs_human_review}")

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
