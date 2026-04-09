import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import TypedDict
import os
from dotenv import load_dotenv

load_dotenv("d:\\project\\AI Agent\\.env")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your_key")

class EvalModel(BaseModel):
    summary: str
    is_safe: bool

class State(TypedDict):
    input: str
    output: EvalModel

def my_node(state: State):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    llm_structured = llm.with_structured_output(EvalModel)
    res = llm_structured.invoke(state["input"])
    return {"output": res}

async def main():
    builder = StateGraph(State)
    builder.add_node("my_node", my_node)
    builder.add_edge(START, "my_node")
    builder.add_edge("my_node", END)
    graph = builder.compile()

    async for event in graph.astream_events({"input": "Hello"}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            node_name = event.get("metadata", {}).get("langgraph_node", "")
            print(f"Stream chunk: {event['data']['chunk'].content[:20]}... | Parent Graph Node: {node_name}")

if __name__ == "__main__":
    asyncio.run(main())
