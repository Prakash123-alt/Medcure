"""Start the Hierarchical Agent API server."""
import uvicorn
import sys
from pathlib import Path

# Add project root to path so hierarchical_agent module can be found
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    uvicorn.run(
        "hierarchical_agent.test_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
