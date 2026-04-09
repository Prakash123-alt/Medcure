# Medical AI Agent - Latency Analysis & Optimization Recommendations

## Current Architecture Overview
- **Service**: `medical-ai-agent` (Cloud Run, us-central1)
- **Resources**: 2 vCPU, 2GB RAM
- **Framework**: LangGraph with 5-layer pipeline (Summarizer → Triage → Context Retrieval → RAG → Reasoning → Persona → Safety)

---

## Identified Bottlenecks (Ranked by Impact)

### 🔴 **CRITICAL: Vector Embedding API Calls in `aiims_rag_node`**
**File**: `medical_ai_agent/nodes/clinical_brain.py` (Line ~237)

```python
embeddings = get_embeddings()
query_vector = await embeddings.aembed_query(search_query)  # ← THIS IS SLOW
```

**Problem**:
- Calling Google VertexAI Embeddings API for every RAG query (~500ms-2s per call)
- No caching of embeddings for identical queries
- Called on every L3 reasoning path (Complex/High-Risk triage level)

**Impact**: **+1-2 seconds per request**

**Solution Priority**: **HIGH**
- Implement embedding cache (in-memory TTL or Redis)
- Batch embeddings if multiple queries come in
- Consider using a faster, lightweight embedding model (e.g., ONNX-based)

---

### 🟠 **HIGH: Sequential Database Queries in `context_retrieval_node`**
**File**: `medical_ai_agent/nodes/clinical_brain.py` (Lines 109-184)

**Problem**:
- `_fetch_patient_snapshot()`: Complex 3-table JOIN with aggregations
- Separate query for `semantic_memory` facts
- No connection pooling optimization
- Runs for every L2+ request

**Impact**: **+200-500ms per request**

**Solution Priority**: **HIGH**
- Add query result caching (already has TTL cache for snapshots, extend to memories)
- Optimize SQL queries (remove N+1 queries, use single multi-purpose query)
- Ensure connection pooling is configured

---

### 🟠 **HIGH: Neo4j Graph Traversal in `aiims_rag_node` (Parallel Task)**
**File**: `medical_ai_agent/nodes/clinical_brain.py` (Lines 211-234)

```python
async def get_graph_context():
    # Extracts entities from query
    # Runs MATCH query for EACH entity (up to N queries)
    # LIMIT 10 per query
```

**Problem**:
- Entity extraction via LLM (Gemini) adds latency
- Multiple MATCH queries run sequentially per entity (should be parallelized)
- No graph query caching
- If entity extraction extracts 5+ entities, this could be slow

**Impact**: **+300-800ms per request**

**Solution Priority**: **MEDIUM**
- Cache Neo4j query results for common entity combinations
- Parallelize entity-specific MATCH queries
- Consider using Neo4j's full-text search instead of MATCH + CONTAINS

---

### 🟡 **MEDIUM: Summarizer Node Always Runs First**
**File**: `medical_ai_agent/graph.py` (Line ~187)

```python
# START → Summarizer (Always first to check context length)
workflow.add_edge(START, "summarizer")
```

**Problem**:
- Every request goes through summarizer first
- Could be processing large chat histories unnecessarily
- For L1 (simple) queries, this is overhead

**Impact**: **+100-300ms per request**

**Solution Priority**: **MEDIUM**
- Make summarizer conditional: only run if chat history > threshold
- Skip for L1 requests or known-simple queries

---

### 🟡 **MEDIUM: LLM Invocations (Gemini, DeepSeek)**
**Notes**:
- DeepSeek R1 reasoning in L3 path can take **15-20 seconds** (expected)
- Multiple Gemini calls for entity extraction, search decision,persona generation
- No obvious streaming or parallel LLM calls visible

**Impact**: **+3-5 seconds per complex request**

**Solution Priority**: **LOW** (expected slowness for L3)
- Use streaming for persona generation to show response faster
- Parallelize LLM calls where possible
- Consider caching system prompts

---

## Summary of Latency Breakdown (Estimated)

| Stage | Time | Notes |
|-------|------|-------|
| **L1 (Simple)** | ~2-3s | Triage → Persona |
| **L2 (Midrange)** | ~3-5s | Context + RAG + L2 Reasoning |
| **L3 (Complex)** | ~15-25s | Context + RAG + DeepSeek R1 |
| **Bottleneck layer** | ~2-3s | Vector embedding + Neo4j + DB queries |

---

## Quick Wins (Implement First)

1. **Embedding Cache**: Add TTL in-memory cache for query embeddings
   - Expected improvement: **-500ms to -1.5s**

2. **Snapshot/Memory Cache**: Extend TTL or fix cache eviction
   - Expected improvement: **-200ms to -400ms**

3. **Conditional Summarizer**: Skip for L1 queries
   - Expected improvement: **-100ms to -200ms**

4. **Neo4j Query Optimization**: Use indices, parallelize entity lookups
   - Expected improvement: **-200ms to -400ms**

---

## Monitoring Recommendations

1. Add timing logs at each node entry/exit
2. Track embedding API call latency separately
3. Monitor database query times in PostgreSQL slow query log
4. Set up Cloud Trace integration to visualize critical path

---

## Next Steps
1. Implement embedding cache (priority 1)
2. Optimize database queries (priority 2)
3. Add conditional summarizer (priority 3)
4. Consider horizontal scaling if L3 requests dominate
