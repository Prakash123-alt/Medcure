# CureMate — Project Summary

This document is a complete, self-contained reference for the repository state after the Advanced RAT (Reasoning-Augmented Tools) work. It explains architecture, features, enhancements, packages, data flows, and all public classes/functions so a developer can replicate the project from scratch without reading the source code first.

---

## 1. High-level purpose

CureMate is an advanced medical reasoning toolkit that combines a knowledge graph (Neo4j) and retrieval-augmented text guidance (RAG) with an iterative Reasoning-Augmented Tool (RAT) engine. It performs multi-iteration clinical reasoning, authoritative evidence retrieval, drug-safety extraction, scoring, and produces an auditable clinical assessment that highlights risks and recommended next steps.

This repo contains two main parts:
- `medical_ai_agent/` — original application (left unchanged by the RAT work).
- `curemate_rat/` — the new standalone package (v2.0.0+) implementing the advanced RAT.

---

## 2. Quick start (developer)

Prereqs:
- Python 3.11+ (tested with 3.14.3 in this workspace)
- Git
- Optional: Neo4j (for full KG functionality)

Recommended local setup (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[dev]
```

Run tests (repo root):

```powershell
.\.venv\Scripts\python -m pytest curemate_rat/tests/ -v --tb=short -o "addopts="
```

Run the advanced demo (mock retrievers by default):

```powershell
.\.venv\Scripts\python run_rat_advanced.py
```

To enable live reasoning provider (DeepSeek R1): set `DEEPSEEK_API_KEY` in `.env` or environment.

To enable Neo4j-based retrievals set these environment variables:
- `NEO4J_URI` (e.g. `bolt://localhost:7687` or `neo4j+s://...`)
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- optional: `NEO4J_DATABASE` (defaults to `neo4j`)

Seed the knowledge graph (example):

```python
# seed_neo4j.py (example)
import asyncio
from neo4j import AsyncGraphDatabase
from curemate_rat.knowledge.seed import seed_knowledge_graph

async def run():
    uri = os.environ['NEO4J_URI']
    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASSWORD']
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    async with driver.session(database=os.getenv('NEO4J_DATABASE','neo4j')) as s:
        await seed_knowledge_graph(driver)

asyncio.run(run())
```

---

## 3. Repo architecture / components

- `curemate_rat/` — main package implementing RAT v2.
  - `__init__.py` exposes public API.
  - `config.py` — RATConfig definitions, prompt templates and provider factories.
  - `models.py` — Pydantic domain models for steps, findings, citations, and result payloads.
  - `engine.py` — `RATEngine` orchestration: iterative think/retrieve/assess loop, evidence management, retries.
  - `retrievers/` — retriever implementations:
    - `base.py` — `BaseRetriever` ABC
    - `callback.py` — `CallbackRetriever` adapter to wrap simple callables
    - `neo4j_medical.py` — `Neo4jMedicalRetriever` for structured KG queries (lazy driver init)
    - `composite.py` — `CompositeRetriever` to fan-out to multiple retrieval sources and score/deduplicate results
  - `providers/` — LLM provider interfaces and implementations (DeepSeek, Mock)
  - `knowledge/` — knowledge graph helpers (schema, seed, parameterized queries)
  - `adapters/` — `medcure.py` adapter to wire retrievers + engine for production/demo
  - `tests/` — unit & integration tests for retrievers, engine, knowledge schema, and models
  - `_logging.py` — correlation id and structured logging helpers
  - `exceptions.py` — defined exception types
  - `run_rat_advanced.py` — advanced demo script using mock retrievers when Neo4j/DeepSeek not configured

---

## 4. Main features & enhancements (summary)

1. Knowledge graph (Neo4j) schema and seed data:
   - Constraints and indexes to support Drugs, Conditions, Enzymes, DrugClass, Allergy and Guideline nodes.
   - Seed includes ~50 drugs, drug-drug interactions, CYP450 metabolism data, contraindications, allergy cross-reactivity, treatment relationships, and dose adjustments.
2. `Neo4jMedicalRetriever`:
   - Runs parameterized Cypher queries for interactions, CYP450, contraindications, allergies, dosage adjustments.
   - Lazy driver init and graceful degradation when Neo4j is unavailable.
3. `CompositeRetriever`:
   - Fan-out queries to multiple retrievers concurrently with per-retriever weight and timeout.
   - Produces scored evidence (`ScoredEvidence`) with source, evidence_type, and numeric score.
   - Deduplicates using Jaccard similarity.
4. Evidence scoring heuristic:
   - Base weight per retriever + severity boost + evidence level boost + source reliability boost + length normalization.
   - Configurable thresholds to decide how many items to return.
5. Enhanced `RATEngine` (v2):
   - Multi-retriever support, tracks `evidence_citations` and `drug_safety_findings`.
   - `_get_scored_evidence()` for structured evidence collection.
   - `_parse_safety_finding()` to extract structured `DrugSafetyFinding` from KG evidence snippets.
   - Prompt assembly that separates `DRUG SAFETY FINDINGS` and `GUIDELINE EVIDENCE` blocks.
   - `max_retries` with exponential backoff for provider calls.
6. Detailed Pydantic models:
   - `ThinkStep`, `FinalAssessment`, `RATResult`, `EvidenceCitation`, `DrugSafetyFinding` — all serializable and designed to be stored/audited.
7. Tests: ~59 unit tests covering engine, retrievers, composite scoring, knowledge graph queries, and models.
8. Demo: `run_rat_advanced.py` demonstrating mock KG + RAG retrieval and full assessment flow.
9. CI-friendly design: tests use pytest/pytest-asyncio and avoid hard-coded external systems by providing mocks and graceful fallbacks.

---

## 5. Detailed file & API reference (go-to guide)

Below are the key modules, classes, and functions with short signatures and clear descriptions. Use these as your mental map when replicating or extending the repo.

### 5.1 `curemate_rat/config.py`
- RATConfig (Pydantic model)
  - Fields: `provider`, `max_iterations`, `confidence_threshold`, `max_retries`, prompt templates, provider-specific settings.
  - Factories: `from_env()`, `from_deepseek(api_key, ...)`, `for_testing()`.
  - Purpose: central place for tuning RAT behaviour and provider wiring.

### 5.2 `curemate_rat/models.py`
Important models and fields (all serializable):
- `ThinkStep`:
  - `iteration: int`
  - `partial_reasoning: str`
  - `confidence: float` (0-1)
  - `retrieval_query: str | None`
  - `knowledge_gaps: list[str]`
  - `evidence_used: list[str]` (added v2)
- `EvidenceCitation`:
  - `text: str`, `source: str`, `score: float`, `evidence_type: str`
- `DrugSafetyFinding`:
  - `finding_type: str` (e.g. 'interaction', 'contraindication', 'allergy', 'dose_adjustment')
  - `drug1: str`, `drug2: str | None`, `severity: str`, `detail: str`, `mechanism: str | None`, `recommendation: str | None`, `source: str`, `evidence_level: str`
- `FinalAssessment`:
  - `assessment_summary: str`, `confidence: float`, `risks_identified: list[str]`, `red_flags: list[str]`, `triage_instructions: str`, `evidence_citations: list[EvidenceCitation]`, `drug_safety_findings: list[DrugSafetyFinding]`, `needs_human_review: bool`
- `RATResult`:
  - `provider_used: str`, `total_iterations: int`, `duration_seconds: float`, `correlation_id: str`, `evidence_collected: list[str]`, `evidence_sources: Dict[str,int]`, `drug_safety_summary: Dict[str,int]`, `think_steps: list[ThinkStep]`, `assessment: FinalAssessment`

### 5.3 `curemate_rat/providers/base.py`
- `class BaseLLMProvider(ABC)`
  - `async def think(self, prompt: str) -> ThinkStep` — returns partial reasoning with a confidence score.
  - `async def assess(self, prompt: str) -> FinalAssessment` — returns a clinical assessment (structured fields).
  - `@classmethod def from_env(cls, ...) -> BaseLLMProvider` — construct provider from env vars.

### 5.4 `curemate_rat/providers/deepseek.py` and `providers/mock.py`
- `DeepSeekProvider` implements `think()` and `assess()` using the live DeepSeek R1 API.
- `MockProvider` returns deterministic outputs for tests.

### 5.5 `curemate_rat/retrievers/base.py`
- `class BaseRetriever(ABC)`
  - `async def retrieve(self, query: str, k: int = 10) -> list[str]`

### 5.6 `curemate_rat/retrievers/neo4j_medical.py`
- `class Neo4jMedicalRetriever(BaseRetriever)`
  - `@classmethod def from_env(cls) -> Neo4jMedicalRetriever` — read `NEO4J_*` env vars.
  - `def set_patient_context(self, conditions: List[str], allergies: List[str], meds: List[str])` — adapt subsequent queries to patient facts.
  - `async def retrieve(self, query: str, k: int = 10) -> list[str]` — maps free-text query to a set of KG Cypher queries and returns human-readable evidence snippets.
  - Internal query runners (each returns list[str]): `_run_drug_interactions(drug_names)`, `_run_cyp450(drug_names)`, `_run_contraindications(conditions)`, `_run_allergy_check(allergies)`, `_run_dosage_adjustments(conditions, drugs)`.
  - Behavior: lazy Neo4j driver creation; if connection fails, logs and degrades gracefully returning an empty list.

### 5.7 `curemate_rat/knowledge/schema.py`
- `SCHEMA_CYPHER` — list of Cypher statements establishing constraints and indexes.
- `async def ensure_schema(driver)` — runs the schema statements.

### 5.8 `curemate_rat/knowledge/seed.py`
- `SEED_CYPHER` — list of batch statements to populate the KG with drugs, interactions, enzymes, conditions and relationships.
- `async def seed_knowledge_graph(driver)` — idempotent seeding function.

### 5.9 `curemate_rat/knowledge/queries.py`
- `class MedicalQueries` — static methods returning `(cypher, params)` tuples for parameterized queries:
  - `drug_drug_interactions(drug_names)`
  - `cyp450_interactions(drug_names)`
  - `contraindication_check(conditions, drugs)`
  - `allergy_check(allergies, drugs)`
  - `treatment_options(condition)`
  - `dosage_adjustments(condition, drug)`
  - `full_safety_scan(patient)` — multi-part query to gather wide evidence
  - `drug_class_for(drug)`
  - `find_alternatives(drug_class, avoid_drugs)`

### 5.10 `curemate_rat/retrievers/composite.py`
- `class CompositeRetriever(BaseRetriever)` — aggregator
  - `add(name: str, retriever: BaseRetriever, weight: float = 1.0, timeout: float | None = None)` — register a sub-retriever with a relative weight and request timeout.
  - `async def retrieve(self, query: str, k: int = 10) -> list[str]` — convenience returning raw strings (weighted top-k).
  - `async def retrieve_scored(self, query: str, k: int = 10) -> list[ScoredEvidence]` — runs fan-out concurrently, applies scoring heuristic, performs Jaccard deduplication, and returns evidence with `score: float`, `source: str`, `evidence_type: str`.
- `ScoredEvidence(dataclass)` — fields: `text: str, score: float, source: str, evidence_type: str`.

Scoring heuristic details (defaults):
- `base_score = retriever.weight`
- `severity_boost = {'severe': +1.0, 'moderate': +0.5, 'minor': +0.1}`
- `evidence_level_boost = {'A': +1.0, 'B': +0.5, 'C': +0.2}`
- `source_reliability` multipliers (e.g., authoritative KG sources > RAG sources)
- `length_normalization = log(1 + len(text))` or similar
- Dedup threshold via Jaccard on token sets (configurable)

### 5.11 `curemate_rat/engine.py` (RATEngine)
- `class RATEngine`:
  - `def __init__(self, config: RATConfig, provider: BaseLLMProvider | None = None, retriever: BaseRetriever | None = None)`
  - `async def run(self, patient_text: str) -> RATResult` — high-level run: iterations of `think()` (asking the model what to retrieve, or forming a retrieval query), calling `retriever` to fetch evidence, then `assess()` to produce a `FinalAssessment` — collects evidence and findings.
  - `_get_scored_evidence(query)` — if retriever is a `CompositeRetriever` returns `ScoredEvidence` list; otherwise adapts the return.
  - `_parse_safety_finding(evidence_snippet: str) -> DrugSafetyFinding | None` — pattern-matching rules that look for prefixes like `[DRUG INTERACTION — SEVERE]` and extract structured fields (drug names, severity, mechanism, recommendation).
  - `_build_assess_prompt(think_summary, evidence_blocks)` — builds a prompt with separate `DRUG SAFETY FINDINGS` and `GUIDELINE EVIDENCE` sections.
  - `_safe_think()` and `_safe_assess()` — wrapper functions that call provider methods with retry/exponential backoff and logging.

Flow summary:
1. Start session (correlation id). 2. For up to `max_iterations`: get `think()` output from provider. 3. If think recommends retrieval, call retriever(s) and collect evidence. 4. If confidence threshold reached, stop retrieving and call `assess()` to build `FinalAssessment`. 5. Parse evidence for structured `DrugSafetyFinding` and produce `RATResult`.

### 5.12 `curemate_rat/adapters/medcure.py`
- `class MedcureRATAdapter` — convenience wrapper used by external apps.
  - `__init__(..., enable_neo4j: bool = True)` — build config and optionally use `Neo4jMedicalRetriever`.
  - `_build_composite_retriever(patient_ctx)` — composes `Neo4jMedicalRetriever` (weight 1.0) + RAG retriever (weight ~0.7) via `CompositeRetriever`.
  - `async def run(patient_case_text)` — runs the `RATEngine` end-to-end and returns `RATResult`.

### 5.13 `run_rat_advanced.py` (demo)
- Demonstrates a complex patient case with mock `DemoGraphRetriever` and `DemoTextRetriever`:
  - Shows evidence audit trail, think steps, drug safety findings, and final clinical assessment.
  - Falls back to `MockProvider` unless `DEEPSEEK_API_KEY` present.

### 5.14 `tests/` (key test files)
- `test_engine.py` — core engine behavior (iteration control, early exit on confidence, result structure).
- `test_models.py` — model validity and serialization.
- `test_providers.py` — provider mocks and deterministic behaviours.
- `test_composite.py` — composite retriever scoring, dedup, timeouts, failure handling.
- `test_knowledge_graph.py` — schema assertions, seed content checks, Cypher query structure tests.
- `test_advanced_engine.py` — integration tests for advanced v2 engine features (safety finding parsing, composite retriever integration).

---

## 6. How to replicate this repo from scratch (step-by-step anchor)

1. Create a project directory and initialize git.

```bash
mkdir curemate && cd curemate
git init
```

2. Create a Python venv and activate it.

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

3. Create `pyproject.toml` and list these dependencies (minimum):
- pydantic>=2.x
- neo4j>=5.x (async driver)
- pytest, pytest-asyncio
- python-dotenv (optional)
- any LLM provider SDKs (DeepSeek SDK if used)

Example `pip` install:

```bash
pip install pydantic neo4j pytest pytest-asyncio python-dotenv
```

4. Add package layout `curemate_rat/` and create modules exactly as described (copy/recreate `config.py`, `models.py`, `engine.py`, `retrievers/`, `providers/`, `knowledge/`, `adapters/`). Follow the API surfaces in this document.

5. Implement tests and run them early to catch integration issues.

6. (Optional) Start a local Neo4j, set environment variables (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`), run the seed script to populate KG.

7. Run `run_rat_advanced.py` to verify the demo output.

---

## 7. Operational notes & runbook

- Logging: `curemate_rat/_logging.py` uses a correlation id; include in production logs for traceability.
- PII: The engine accepts free-text clinical notes; store and transmit with care and in compliance with local regulations.
- Neo4j connections: Use `neo4j+s://` for cloud-hosted instances and ensure TLS is enabled. For large KG datasets, use pagination in queries.
- Provider failures: `RATEngine` retries provider calls up to `max_retries` (configurable). Retrievers time out per their `timeout` parameter and are handled by `CompositeRetriever`.
- Extensibility: Add new retrievers by implementing `BaseRetriever` and registering with `CompositeRetriever.add()`.

---

## 8. Recommended testing & CI

- Run the `curemate_rat/tests/` suite on every PR.
- Mock external systems in CI (mock provider + mock Neo4j responses or use a lightweight in-memory Neo4j fixture if feasible).
- Add linting and formatting (Black, ruff) as CI steps.

---

## 9. Branches & release notes

- A feature branch was created and pushed during development: `feature/advanced-rat-neo4j-demo`.
- Package version (in `curemate_rat/__init__.py`): `v2.0.0`.

---

## 10. Troubleshooting

- If `pytest` shows failures due to env assumptions, run with `-o "addopts="` to ignore repo-level pytest custom addopts that can conflict with CI.
- If Neo4j driver fails to connect, ensure `NEO4J_URI` is reachable and credentials correct; run `neo4j status` and check logs.

---

## 11. Developer API reference (exhaustive quick signatures)

NOTE: these are illustrative method/property shapes; check the actual module if you need exact parameter names.

- RATConfig.from_env() -> RATConfig
- RATEngine(config: RATConfig, provider: BaseLLMProvider|None = None, retriever: BaseRetriever|None = None)
- RATEngine.run(patient_text: str) -> RATResult
- BaseLLMProvider.think(prompt: str) -> ThinkStep
- BaseLLMProvider.assess(prompt: str) -> FinalAssessment
- CompositeRetriever.add(name: str, retriever: BaseRetriever, weight: float = 1.0, timeout: float | None = None)
- CompositeRetriever.retrieve_scored(query: str, k: int = 10) -> list[ScoredEvidence]
- Neo4jMedicalRetriever.from_env() -> Neo4jMedicalRetriever
- Neo4jMedicalRetriever.set_patient_context(conditions: list[str], allergies: list[str], meds: list[str])
- knowledge.schema.ensure_schema(driver) -> None
- knowledge.seed.seed_knowledge_graph(driver) -> None

---

## 12. Security & compliance

- Secrets (API keys, DB credentials) must never be committed. Use `.env` or secret stores in CI/CD.
- Avoid sending PHI to third-party providers unless contractual/technical safeguards are in place.

---

## 13. Next steps & suggestions

- Add a top-level `README.md` that references this `Summary.md` and includes short examples to run the demo, seed KG, and use the adapter.
- Add small scripts: `scripts/seed_neo4j.py`, `scripts/run_demo_local.py` to make reproduction easier.
- Add CI job to run `pytest` and linting on PRs.
- Consider adding a persisted evidence store (Postgres) if audit retention is required.

---

## 14. Contact points in code (where to start reading)

- For engine behaviour, begin at: `curemate_rat/engine.py`
- For retrieval & scoring: `curemate_rat/retrievers/composite.py`
- For KG schema & seed: `curemate_rat/knowledge/schema.py` and `curemate_rat/knowledge/seed.py`
- For demo and usage patterns: `run_rat_advanced.py` and `curemate_rat/adapters/medcure.py`

---

## 15. File index (for convenience)

- curemate_rat/__init__.py
- curemate_rat/config.py
- curemate_rat/models.py
- curemate_rat/engine.py
- curemate_rat/exceptions.py
- curemate_rat/_logging.py
- curemate_rat/providers/base.py
- curemate_rat/providers/deepseek.py
- curemate_rat/providers/mock.py
- curemate_rat/retrievers/base.py
- curemate_rat/retrievers/composite.py
- curemate_rat/retrievers/neo4j_medical.py
- curemate_rat/retrievers/callback.py
- curemate_rat/knowledge/schema.py
- curemate_rat/knowledge/seed.py
- curemate_rat/knowledge/queries.py
- curemate_rat/adapters/medcure.py
- run_rat_advanced.py
- pyproject.toml
- curemate_rat/tests/

---
