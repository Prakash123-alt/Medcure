"""
Test the full agent flow with a real medical query
"""
import asyncio
import sys
import os
import codecs
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hierarchical_agent.graph import get_graph_builder
from hierarchical_agent.hybrid_medical_search import HybridMedicalSearch
from hierarchical_agent.config import HybridSearchConfig

load_dotenv()

async def test_hybrid_search():
    """Test hybrid search component"""
    print("\n" + "="*60)
    print("TEST 1: Hybrid Medical Search")
    print("="*60)
    
    search = HybridMedicalSearch()
    
    # Test queries
    test_queries = [
        ("aspirin side effects", "general"),
        ("metformin", "drug_interaction"),
        ("diabetes treatment", "pubmed"),
        ("ibuprofen recall", "fda_alert")
    ]
    
    for query, search_type in test_queries:
        print(f"\n>>> Query: '{query}' (type: {search_type})")
        print("-" * 60)
        
        results = await search.search(query, search_type)
        
        print(f"Results: {len(results)}")
        if results:
            print(f"Top 3 results:")
            for i, r in enumerate(results[:3]):
                verified = "[V]" if r.verified else "[X]"
                print(f"  {i+1}. {verified} [{r.source}] {r.title[:50]}...")
                print(f"     Score: {r.relevance_score:.2f}")
        else:
            print("  No results found")

async def test_agent_flow():
    """Test the full agent graph flow"""
    print("\n" + "="*60)
    print("TEST 2: Full Agent Flow")
    print("="*60)
    
    # Get the graph
    graph_builder = get_graph_builder()
    app = graph_builder.compile()
    
    # Test query
    test_query = "What are the side effects of aspirin?"
    
    print(f"\n>>> Query: '{test_query}'")
    print("-" * 60)
    
    # Initial state
    initial_state = {
        "query": test_query,
        "user_id": "test_user",
        "lane": "fast_track",
        "lane_reason": "Test query"
    }
    
    # Config with thread ID
    config = {
        "configurable": {
            "thread_id": "test_thread_001"
        }
    }
    
    try:
        # Run the graph
        print("\nRunning agent graph...")
        final_state = await app.ainvoke(initial_state, config=config)
        
        print("\n" + "="*60)
        print("FINAL RESPONSE:")
        print("="*60)
        response = final_state.get("final_response", "No response generated")
        print(response)
        print("="*60)
        
        # Check state
        print(f"\nState Summary:")
        print(f"  Lane: {final_state.get('lane', 'N/A')}")
        print(f"  Search Results: {len(final_state.get('search_results', []))}")
        print(f"  Synthesizer Done: {final_state.get('synthesizer_fast_done', False)}")
        
        # Check search results
        search_results = final_state.get("search_results", [])
        if search_results:
            print(f"\n  Search Results by Source:")
            sources = {}
            for r in search_results:
                # Handle both dict and SearchResult objects
                if isinstance(r, dict):
                    source = r.get("source", "unknown")
                else:
                    source = getattr(r, "source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            for source, count in sources.items():
                print(f"    {source}: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_node_integration():
    """Test individual nodes"""
    print("\n" + "="*60)
    print("TEST 3: Node Integration")
    print("="*60)
    
    from hierarchical_agent.risk_router import risk_router_node
    from hierarchical_agent.planner import planner_node
    from hierarchical_agent.synthesizer_fast import synthesizer_fast_node
    
    # Test risk router
    print("\n>>> Testing Risk Router")
    state = {"query": "I have chest pain"}
    result = await risk_router_node(state)
    print(f"  Lane: {result.get('lane', 'N/A')}")
    print(f"  Reason: {result.get('lane_reason', 'N/A')}")
    
    # Test planner
    print("\n>>> Testing Planner")
    state = {"query": "What are the side effects of metformin?"}
    result = await planner_node(state)
    print(f"  Query Type: {result.get('query_type', 'N/A')}")
    print(f"  Search Queries: {result.get('search_queries', [])}")
    
    print("\n✅ Node integration tests complete")

async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CUREMATE AI - FULL AGENT TEST SUITE")
    print("="*60)
    
    # Show configuration
    print("\nConfiguration Status:")
    status = HybridSearchConfig.get_status()
    for api, info in status.items():
        enabled = "[ON]" if info["enabled"] else "[OFF]"
        configured = "[YES]" if info["configured"] else "[NO]"
        print(f"  {api.upper()}: {enabled} {configured}")
    
    try:
        # Test 1: Hybrid Search
        await test_hybrid_search()
        
        # Test 2: Node Integration
        await test_node_integration()
        
        # Test 3: Full Agent Flow
        success = await test_agent_flow()
        
        print("\n" + "="*60)
        if success:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
