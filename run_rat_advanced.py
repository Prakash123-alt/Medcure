#!/usr/bin/env python
"""
CureMate RAT — Advanced Medical Demo (v2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Demonstrates the full advanced medical RAT pipeline:
  1. CompositeRetriever combining mock Neo4j graph + mock text retrievers
  2. Drug safety finding extraction from structured evidence
  3. Evidence scoring & ranking
  4. Medical-tuned prompts

Run:  python run_rat_advanced.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass


# ── Mock retrievers (for demo without Neo4j running) ────────────────────

from curemate_rat.retrievers.base import BaseRetriever


class DemoGraphRetriever(BaseRetriever):
    """Simulates Neo4j KG evidence for the demo patient."""

    async def retrieve(self, query: str, k: int = 10) -> list[str]:
        # Simulate what the real Neo4j retriever would return
        return [
            "[DRUG INTERACTION — SEVERE] Aspirin + Warfarin: Significantly increased bleeding risk. "
            "Mechanism: Both affect coagulation cascade. "
            "Recommendation: Monitor INR closely. Consider reducing warfarin dose. "
            "(Source: FDA, Evidence: A)",

            "[CONTRAINDICATION — SEVERE] Metformin in Chronic Kidney Disease (ICD-10: N18): "
            "Metformin accumulates — lactic acidosis risk with impaired renal clearance. "
            "Recommendation: Contraindicated if eGFR < 30. Reduce dose 50% if eGFR 30-45. "
            "(Source: AIIMS, Evidence: A)",

            "[ALLERGY — CONTRAINDICATED] Amoxicillin: Amoxicillin belongs to a drug class "
            "that cross-reacts with Penicillin_Allergy. "
            "Cross-reactive classes: Penicillin, Cephalosporin. "
            "DO NOT PRESCRIBE. Find alternative medication.",

            "[CYP450 CONFLICT] Amiodarone is a inhibitor of CYP3A4, which metabolises Simvastatin. "
            "Predicted effect: Increased Simvastatin levels — toxicity risk. "
            "Recommendation: Monitor for Simvastatin toxicity. Consider dose reduction.",

            "[DOSE ADJUSTMENT] Digoxin in Chronic Kidney Disease "
            "(renal population, factor: eGFR): "
            "Reduce dose. Target trough 0.5-0.9 ng/mL.",

            "[DOSE ADJUSTMENT] Enoxaparin in Chronic Kidney Disease "
            "(renal population, factor: CrCl): "
            "CrCl<30: reduce to 1mg/kg daily (not BID).",
        ]


class DemoTextRetriever(BaseRetriever):
    """Simulates AIIMS guidelines RAG retrieval."""

    async def retrieve(self, query: str, k: int = 10) -> list[str]:
        return [
            "AIIMS Guideline (Community-Acquired Pneumonia in Elderly): "
            "First-line: Azithromycin 500mg OD × 5 days OR Amoxicillin-Clavulanate 625mg TID × 7 days. "
            "Alternative for penicillin-allergic: Levofloxacin 500mg OD × 7 days. "
            "Caution: Fluoroquinolones may lower seizure threshold — avoid in epilepsy.",

            "AIIMS Protocol (Diabetes Management with CKD): "
            "eGFR > 45: Metformin safe at full dose. "
            "eGFR 30-45: Reduce metformin to 500mg BID max. "
            "eGFR < 30: STOP metformin. Use DPP4 inhibitors (sitagliptin adjusted to 25mg) or insulin. "
            "SGLT2 inhibitors: Hold if eGFR < 20.",
        ]


# ── Demo ────────────────────────────────────────────────────────────────

COMPLEX_PATIENT = """\
PATIENT HISTORY:
  Age: 68, Gender: Male
  BMI: 28.5
  Renal Function (CrCl): 35 mL/min (eGFR approximately 32)
  Conditions: Type 2 Diabetes Mellitus, Chronic Kidney Disease (Stage 3b),
              Atrial Fibrillation, Coronary Artery Disease
  Allergies: Penicillin
  Current Meds: Digoxin 0.25mg OD, Warfarin 5mg OD, Atorvastatin 40mg OD,
                Amlodipine 5mg OD

CURRENT PRESCRIPTION:
  Symptoms: Fever (38.5°C), productive cough, chest discomfort, fatigue
  Medicines: Amoxicillin 500mg TID, Metformin 1000mg BID,
             Aspirin 75mg OD, Pantoprazole 40mg OD
"""


async def main():
    from curemate_rat.config import RATConfig
    from curemate_rat.engine import RATEngine
    from curemate_rat.retrievers.composite import CompositeRetriever

    print("=" * 70)
    print("  CureMate RAT v2 — Advanced Medical Reasoning Demo")
    print("=" * 70)

    # Determine provider
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if api_key:
        print(f"\n  Provider: DeepSeek R1 (live API)")
        cfg = RATConfig.from_deepseek(
            api_key,
            max_iterations=4,
            confidence_threshold=0.80,
            max_retries=2,
        )
    else:
        print(f"\n  Provider: Mock (set DEEPSEEK_API_KEY for live reasoning)")
        cfg = RATConfig(
            provider="mock",
            max_iterations=3,
            confidence_threshold=0.85,
            max_retries=1,
        )

    # Build composite retriever
    composite = CompositeRetriever()
    composite.add("neo4j_kg", DemoGraphRetriever(), weight=1.0, timeout=10.0)
    composite.add("aiims_rag", DemoTextRetriever(), weight=0.7, timeout=10.0)

    print(f"  Retrievers: {composite.source_count} sources (Neo4j KG + AIIMS RAG)")
    print(f"  Max iterations: {cfg.max_iterations}")
    print(f"  Confidence threshold: {cfg.confidence_threshold}")
    print()
    print("─" * 70)
    print("PATIENT CASE:")
    print("─" * 70)
    print(COMPLEX_PATIENT)

    # Run
    engine = RATEngine(cfg, retriever=composite)
    print("─" * 70)
    print("RUNNING RAT ENGINE...")
    print("─" * 70)

    result = await engine.run(COMPLEX_PATIENT)

    # Display results
    print()
    print("═" * 70)
    print("  RAT RESULTS")
    print("═" * 70)

    print(f"\n  Provider: {result.provider_used}")
    print(f"  Iterations: {result.total_iterations}")
    print(f"  Duration: {result.duration_seconds:.2f}s")
    print(f"  Correlation ID: {result.correlation_id}")
    print(f"  Evidence collected: {len(result.evidence_collected)} snippets")
    print(f"  Evidence sources: {result.evidence_sources}")
    print(f"  Drug safety summary: {result.drug_safety_summary}")

    # Think steps
    print()
    print("─" * 70)
    print("THINK STEPS:")
    print("─" * 70)
    for step in result.think_steps:
        print(f"\n  Iteration {step.iteration}: confidence={step.confidence:.2f}")
        print(f"    Reasoning: {step.partial_reasoning[:200]}...")
        if step.knowledge_gaps:
            print(f"    Gaps: {step.knowledge_gaps[:3]}")
        if step.retrieval_query:
            print(f"    Query: {step.retrieval_query[:100]}")
        if step.evidence_used:
            print(f"    Evidence used: {len(step.evidence_used)} snippets")

    # Drug safety findings
    findings = result.assessment.drug_safety_findings
    if findings:
        print()
        print("─" * 70)
        print(f"DRUG SAFETY FINDINGS ({len(findings)} total):")
        print("─" * 70)
        for f in findings:
            icon = {"contraindicated": "🚫", "severe": "🔴", "moderate": "🟡", "minor": "🟢"}.get(
                f.severity, "⚪"
            )
            print(f"\n  {icon} [{f.severity.upper()}] {f.finding_type}")
            print(f"     Drug: {f.drug1}" + (f" + {f.drug2}" if f.drug2 else ""))
            print(f"     Detail: {f.detail[:150]}")
            if f.mechanism:
                print(f"     Mechanism: {f.mechanism}")
            if f.recommendation:
                print(f"     Recommendation: {f.recommendation[:150]}")

    # Evidence citations
    citations = result.assessment.evidence_citations
    if citations:
        print()
        print("─" * 70)
        print(f"EVIDENCE AUDIT TRAIL ({len(citations)} citations):")
        print("─" * 70)
        for i, c in enumerate(citations[:10], 1):
            print(f"\n  [{i}] Source: {c.source} | Score: {c.score:.3f} | Type: {c.evidence_type}")
            print(f"      {c.text[:120]}...")

    # Final assessment
    print()
    print("═" * 70)
    print("FINAL CLINICAL ASSESSMENT")
    print("═" * 70)
    a = result.assessment
    print(f"\n  Confidence: {a.confidence:.2f}")
    print(f"  Needs Human Review: {a.needs_human_review}")
    print(f"\n  Summary:\n    {a.assessment_summary[:500]}")
    if a.risks_identified:
        print(f"\n  Risks ({len(a.risks_identified)}):")
        for r in a.risks_identified[:10]:
            print(f"    • {r}")
    if a.red_flags:
        print(f"\n  🚨 RED FLAGS:")
        for rf in a.red_flags:
            print(f"    ‼ {rf}")
    if a.triage_instructions:
        print(f"\n  Triage: {a.triage_instructions[:300]}")

    print()
    print("═" * 70)
    print("  Demo complete.")
    print("═" * 70)


if __name__ == "__main__":
    asyncio.run(main())
