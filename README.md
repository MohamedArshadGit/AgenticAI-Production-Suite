# 🤖 CHATBOT — Modular Agentic AI System

> A production-grade, modular agentic chatbot built phase by phase using LangGraph, ChatGroq, and Streamlit. Designed as a portfolio project that grows from a basic chatbot into a full multi-agent system with tools, memory, RAG, GraphRAG, evaluation, and cloud deployment.

---

## 📊 Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Basic chatbot — LangGraph loop + Streamlit UI | ✅ Done |
| **Phase 2** | 3-layer observability — JSON logger + LangSmith + BaseCallbackHandler | ✅ Done |
| **Phase 3** | Tools + ReAct agent — MCP server + 7 tools + async + parallel tool calling | ✅ Done |
| **Phase 4** | Router + Human-in-the-loop | ⏳ Next |
| **Phase 5** | Orchestrator-worker multi-agent | ⏳ Planned |
| **Phase 6** | Redis memory — persistent sessions | ⏳ Planned |
| **Phase 7** | Multi-Agent Microservices (A2A) | ⏳ Planned |
| **Phase 8** | MCP Full Integration | ⏳ Planned |
| **Phase 9** | DeepEval + RAGAS evaluation | ⏳ Planned |
| **Phase 10** | Hybrid GraphRAG — Neo4j + Pinecone | ⏳ Planned |
| **Phase 11** | Docker + CI/CD + Cloud deploy | ⏳ Planned |

---

## 📁 Project Structure

```
CHATBOT/
├── logs/
│   └── app.log
├── src/
│   ├── app.py                          # Entry point / launcher
│   └── langgraph_agenticai/
│       ├── main.py                     # Core app logic
│       │
│       ├── graph/
│       │   └── graph_builder.py        # LangGraph workflow + ReAct loop
│       │
│       ├── llms/
│       │   └── groqllm.py              # ChatGroq initialisation
│       │
│       ├── nodes/
│       │   ├── basic_chatbot_node.py   # Phase 1 node
│       │   ├── agent_node.py           # ReAct agent node (Phase 3)
│       │   └── tool_node.py            # Tool executor node (Phase 3)
│       │
│       ├── state/
│       │   └── state.py                # TypedDict state definition
│       │
│       ├── tools/
│       │   ├── calculator_tool.py      # SymPy math
│       │   ├── currency_tool.py        # ExchangeRate API
│       │   ├── datetime_tool.py        # pytz timezone datetime
│       │   ├── file_tool.py            # Local file reader
│       │   ├── location_tool.py        # IP geolocation
│       │   ├── search_tool.py          # Tavily web search
│       │   ├── weather_tool.py         # OpenWeatherMap
│       │   └── mcp_server/
│       │       └── tool_server.py      # FastMCP server (localhost:8000/mcp)
│       │
│       ├── ui/
│       │   └── streamlitui/
│       │       ├── loadui.py
│       │       └── display_result.py
│       │
│       ├── utils/
│       │   └── logger.py               # JSON structured logger
│       │
│       └── tests/
│           ├── test.py
│           └── test_graph_visualise.py
│
├── .env
├── .gitignore
└── README.md
```

### Structure Rules (Applied Across All Phases)

- **One file, one job** — every file has a single responsibility
- **Build order** — `state` → `nodes` → `graph` → `llms` → `ui` → `main`
- **Dependencies via constructor** — never import globally, pass via `__init__`
- **Every node** has `__init__(self, model)` and `process(self, state) -> dict`

---

## ✅ Phase 1 — Basic Chatbot

### What it does

- Accepts user messages via Streamlit UI
- Passes them through a LangGraph `StateGraph`
- `BasicChatbotNode` calls ChatGroq and returns a response
- Maintains conversation history in state across turns

### Architecture

```
User input (Streamlit)
        │
        ▼
  State { messages: [...] }
        │
        ▼
  BasicChatbotNode (ChatGroq LLM)
        │
        ▼
  Updated state { messages: [..., AIMessage] }
        │
        ▼
  Response displayed in Streamlit
```

---

## ✅ Phase 2 — 3-Layer Observability

### What it does

Adds three independent observability layers that run on every node execution.

| Layer | Tool | What it captures |
|-------|------|-----------------|
| **Layer 1** | Custom JSON logger (`utils/logger.py`) | Node entry, exit, errors — written to `logs/app.log` |
| **Layer 2** | LangSmith tracing | Full chain traces, token usage, latency — LangSmith dashboard |
| **Layer 3** | `BaseCallbackHandler` | `on_llm_start`, `on_llm_end`, `on_tool_start`, `on_tool_end` hooks |

### Log Format (Layer 1)

```json
{
  "time": "2026-03-23T09:13:10.881443",
  "level": "INFO",
  "node": "AgentNode",
  "msg": "LLM decided to call tools",
  "data": { "tools": ["calculator_tool", "weather_tool"] }
}
```

### Environment Variables

```env
GROQ_API_KEY=your_groq_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=CHATBOT
```

---

## ✅ Phase 3 — Tools + ReAct Agent (MCP + Async + Parallel Tool Calling)

### What it does

Transforms the basic chatbot into a true agentic system with 7 production tools, an MCP server, async execution, and a ReAct reasoning loop.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **ReAct Loop** | LLM decides: reply directly OR call one/many tools. Tool results feed back to LLM until final answer |
| **Parallel Tool Calling** | Multiple tools called simultaneously in one LLM response via `tool_calls` list in `AIMessage` |
| **Async Architecture** | All MCP tools are async. `ToolNode` bridges sync LangGraph with async tools via `asyncio.run(tool.ainvoke(args))` |
| **MCP Decoupling** | Tools run in a separate FastMCP server. Agent connects dynamically — add/remove tools without touching agent code |
| **Self-Correction** | LLM reads tool errors and retries with corrected arguments automatically |
| **Recursion Protection** | `recursion_limit=10` in graph config prevents infinite loops |

---

### 7 Tools Implemented

| Tool | API / Library | Description |
|------|--------------|-------------|
| `calculator_tool` | SymPy | Safe mathematical expression evaluation |
| `currency_converter_tool` | ExchangeRate API (free, no key) | Live currency conversion |
| `datetime_tool` | pytz | Timezone-aware current date and time |
| `file_tool` | Python built-in `open()` | Reads local text files (.txt, .csv, .json, .py, .md) |
| `location_tool` | ip-api.com (free) | IP-based geolocation |
| `search_tool` | Tavily API | Live web search for current events |
| `weather_tool` | OpenWeatherMap API | Current weather by city or coordinates |

---

### MCP Server Architecture

Tools are not imported directly by the agent. They are exposed via a **FastMCP server** running independently on `localhost:8000`.

```
Agent (main.py)
    │
    │  await client.get_tools()
    ▼
MultiServerMCPClient ──── HTTP ────► FastMCP Server (localhost:8000/mcp)
                                            │
                                    @mcp.tool() calculator_tool
                                    @mcp.tool() weather_tool
                                    @mcp.tool() search_tool
                                    @mcp.tool() ...7 tools
```

**Why MCP instead of direct imports:**

| Direct Import | Via MCP Server |
|--------------|----------------|
| Agent tightly coupled to tools | Agent loosely coupled |
| Add tool → modify agent code | Add tool → update server only |
| One agent per tool set | Multiple agents share same server |
| Can't scale independently | Tools scale independently |

**Transport:** StreamableHTTP (`/mcp` endpoint) — Anthropic's current recommended MCP transport, replacing legacy SSE.

**Start the server:**
```bash
python src/langgraph_agenticai/tools/mcp_server/tool_server.py
# Output: Uvicorn running on http://127.0.0.1:8000
```

---

### ReAct Graph Flow

```
START
  │
  ▼
agent_node  ◄──────────────────────────┐
  │                                    │
  │  should_use_tool()                 │
  ├── tool_calls exist ──► tool_node ──┘
  │                        (executes tools,
  │                         returns ToolMessage)
  └── no tool_calls ──► END
        (direct reply)
```

**Edges:**
- `START → agent` — always
- `agent → tools` — conditional (`should_use_tool` returns `"tools"`)
- `agent → END` — conditional (`should_use_tool` returns `"end"`)
- `tools → agent` — always (loop back with tool results)

---

### Async Architecture

```python
# MCP client fetch (async)
client = MultiServerMCPClient({...})
tools = await client.get_tools()   # fetches 7 tools from server

# ToolNode execution (bridges sync LangGraph → async MCP tools)
result = asyncio.run(tool.ainvoke(tool_args))

# Streamlit bridge (sync UI → async MCP)
tools = asyncio.run(get_tools_from_mcp())
```

---

### Self-Correction in Action (Real Example)

```
User: "What is the weather in Tirunelveli?"

Round 1:
  Agent calls → weather_tool(city="Tirunelveli")
  Tool fails  → pydantic validation error: latitude/longitude must be float, got None

Round 2:
  LLM reads error → infers coordinates: lat=8.4, lon=77.6
  Agent calls → weather_tool(city="Tirunelveli", latitude=8.4, longitude=77.6)
  Tool succeeds → Temperature: 35.6°C, clear sky ✅

Zero code changes. Pure ReAct reasoning.
```

---

### Observability — Extended for Phase 3

| Layer | What it now captures |
|-------|---------------------|
| **JSON Logger** | Tool name, args, result at `ToolNode` level |
| **LangSmith** | Full graph trace including tool call latency |
| **CallbackHandler** | `on_tool_start` / `on_tool_end` fires automatically |

---

### Key Files (Phase 3)

| File | Purpose |
|------|---------|
| `nodes/agent_node.py` | Binds tools to LLM via `bind_tools()`, runs LLM, returns tool call or direct reply |
| `nodes/tool_node.py` | Reads `tool_calls` from `AIMessage`, looks up tool by name, executes via `ainvoke()` |
| `tools/*.py` | 7 individual `@tool` decorated functions |
| `tools/mcp_server/tool_server.py` | FastMCP server exposing all 7 tools via `@mcp.tool()` |
| `graph/graph_builder.py` | Updated with `add_conditional_edges` and `tools → agent` loop |
| `main.py` | Fetches tools from MCP via `asyncio.run(get_tools_from_mcp())` before building graph |

---

### New Environment Variables (Phase 3)

```env
TAVILY_API_KEY=your_tavily_key
OPENWEATHER_API_KEY=your_openweather_key
```

### How to Run (Phase 3)

```bash
# Terminal 1 — start MCP server
python src/langgraph_agenticai/tools/mcp_server/tool_server.py

# Terminal 2 — start Streamlit
streamlit run src/app.py

# In UI — select "Tools + ReAct" usecase
```

---

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/MohamedArshadGit/MultiAgent-LLM-Agent-Orchestrator_lab.git
cd MultiAgent-LLM-Agent-Orchestrator_lab/CHATBOT

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Fill in your API keys
```

---

## 🔑 API Keys

| Key | URL | Free Tier |
|-----|-----|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✅ Free |
| `LANGCHAIN_API_KEY` | [smith.langchain.com](https://smith.langchain.com) | ✅ Free tier |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | ✅ 1000/month |
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | ✅ 1000/day |

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | ChatGroq (Llama 3.1 8B / 70B) |
| Agent Framework | LangGraph |
| LLM Toolkit | LangChain |
| UI | Streamlit |
| Observability | LangSmith + JSON logger + BaseCallbackHandler |
| Tool Protocol | FastMCP + StreamableHTTP |
| Web Search | Tavily API |
| Weather | OpenWeatherMap API |
| Math | SymPy |
| Language | Python 3.11+ |
| **Coming** | |
| Memory | Redis + RedisChatMessageHistory |
| Vector DB | Pinecone |
| Graph DB | Neo4j + NetworkX |
| Evaluation | DeepEval + RAGAS |
| Containerisation | Docker + Kubernetes |
| CI/CD | GitHub Actions |
| Cloud | AWS / Azure |

---

## 🗺️ Roadmap Detail

### Phase 4 — Router + HITL
- Router node classifies user intent → routes to right sub-graph
- `interrupt()` pauses graph before sensitive actions
- User confirms or cancels in Streamlit UI

### Phase 5 — Orchestrator-Worker
- Planner LLM breaks complex task into subtasks
- Worker agents run in parallel (each a compiled sub-graph)
- Orchestrator synthesises final answer

### Phase 6 — Redis Memory
- Username in sidebar → `session_id`
- `RedisChatMessageHistory` persists conversation per user across restarts

### Phase 7 — Multi-Agent Microservices (A2A)
- Each agent runs as a FastAPI microservice on its own port
- Agents communicate via A2A protocol
- Supervisor coordinates via `ICSRState` and conditional edges

### Phase 8 — MCP Full Integration
- MCP Resources — agent reads files and DBs via MCP
- MCP Prompts — reusable prompt templates
- External MCP servers — GitHub, Slack, etc.

### Phase 9 — DeepEval + RAGAS
- Node-level unit tests: hallucination, correctness, relevancy
- RAG metrics: faithfulness, context precision, context recall
- CI/CD integration — tests on every push

### Phase 10 — Hybrid GraphRAG
- Extract entities and relationships from documents
- Neo4j (production) + NetworkX (dev)
- Hybrid retrieval: graph traversal + Pinecone vector similarity

### Phase 11 — Docker + CI/CD + Cloud
- Dockerfile + docker-compose
- GitHub Actions pipeline: test → build → push → deploy
- AWS Bedrock / Azure OpenAI

---

## 👤 Author

**Mohamed Arshad**  
AI Engineer — Crawley, UK  
[github.com/MohamedArshadGit](https://github.com/MohamedArshadGit)

---

## 🔗 Related Projects

- [`RAG_Lab`](https://github.com/MohamedArshadGit/RAG_Lab) — RAG pipeline experiments
- [`MultiAgent-LLM-Agent-Orchestrator_lab`](https://github.com/MohamedArshadGit/MultiAgent-LLM-Agent-Orchestrator_lab) — Multi-agent orchestration patterns

---

*Built phase by phase as a daily practice and portfolio centrepiece. Each phase is a self-contained, production-grade addition — not a throwaway prototype.*