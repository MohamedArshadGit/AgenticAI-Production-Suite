# tests/test_graph_visualise.py

import sys
import os
sys.path.append(
    r"C:\Users\Mohamed Arshad\Downloads\My_RAG_Lab\MultiAgent-LLM-Agent-Orchestrator_lab\CHATBOT\src"
)

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langgraph_agenticai.graph.graph_builder import GraphBuilder
from langgraph_agenticai.tools.datetime_tool import get_datetime
from langgraph_agenticai.tools.calculator_tool import calculator
from langgraph_agenticai.tools.location_tool import get_location
from langgraph_agenticai.tools.search_tool import search_web
from langgraph_agenticai.tools.weather_tool import get_weather
from langgraph_agenticai.tools.file_tool import file_reader_tool
from langgraph_agenticai.tools.currency_tool import currency_converter

# ── tools list ──────────────────────────────────────────────
tools = [
    get_datetime,
    calculator,
    get_location,
    search_web,
    get_weather,
    file_reader_tool,
    currency_converter
]

# ── build LLM directly (no UI needed) ───────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# ── build graph ─────────────────────────────────────────────
#graph = GraphBuilder(llm).setup_graph("Tools + ReAct ", tools=tools)

graph = GraphBuilder(llm).setup_graph("Tools + ReAct + HITL", tools=tools)

png_bytes = graph.get_graph().draw_mermaid_png()
output_path = r"C:\Users\Mohamed Arshad\Downloads\My_RAG_Lab\MultiAgent-LLM-Agent-Orchestrator_lab\CHATBOT\src\langgraph_agenticai\tests\graph_visual.png"
with open(output_path, "wb") as f:
    f.write(png_bytes)
print(f"✅ Graph saved to {output_path} — open it to see the graph")