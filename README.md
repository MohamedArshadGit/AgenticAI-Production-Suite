# CHATBOT — Modular Agentic Chatbot (LangGraph + ChatGroq)

> A production-grade, modular agentic chatbot built phase by phase using LangGraph, ChatGroq, and Streamlit. Designed as a portfolio project that grows from a basic chatbot into a full multi-agent system with tools, memory, RAG, GraphRAG, evaluation, and cloud deployment.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Basic chatbot — LangGraph loop + Streamlit UI | ✅ Done |
| Phase 2 | 3-layer logging — JSON logger + LangSmith + BaseCallbackHandler | ✅ Done |
| Phase 3 | Tools + ReAct agent — calculator, datetime, web search, weather, news, file reader | 🔄 Next |
| Phase 4 | Router + Human-in-the-loop | ⏳ Planned |
| Phase 5 | Orchestrator-worker multi-agent | ⏳ Planned |
| Phase 6 | Redis memory — username-based persistent sessions | ⏳ Planned |
| Phase 7 | RAG + Corrective RAG + Adaptive RAG | ⏳ Planned |
| Phase 8 | GraphRAG — NetworkX → Neo4j | ⏳ Planned |
| Phase 9 | DeepEval + RAGAS evaluation | ⏳ Planned |
| Phase 10 | Docker + Kubernetes + CI/CD + Cloud deploy | ⏳ Planned |

---

## Project Structure

```
CHATBOT/
├── state/
│   └── chatbot_state.py          # TypedDict state shared across all nodes
├── nodes/
│   ├── __init__.py
│   └── chatbot_node.py           # Core node — every node has __init__(model) + process(state)
├── graph/
│   └── graph_builder.py          # Builds and compiles the LangGraph StateGraph
├── llms/
│   └── llm_factory.py            # LLM initialisation (ChatGroq)
├── streamlitui/
│   └── app.py                    # Streamlit frontend
├── utils/
│   └── logger.py                 # Structured JSON logger
├── tests/
│   └── test_chatbot_node.py      # DeepEval + RAGAS tests (Phase 9)
├── logs/
│   └── chatbot.log               # Auto-generated JSON log file
├── main.py                       # Entry point
├── .env                          # API keys (never commit)
├── .env.example                  # Template for environment variables
├── requirements.txt
└── README.md
```

### Structure rules (applied across all phases)
- **One file, one job** — every file has a single responsibility
- **Build order** — state → nodes → graph → llms → ui → main
- **Dependencies via `__init__`** — never import globally, pass via constructor
- **Every node** has `__init__(self, model)` and `process(self, state) -> dict`

---

## Phase 1 — Basic Chatbot

### What it does
- Accepts user messages via Streamlit UI
- Passes them through a LangGraph `StateGraph`
- `ChatbotNode` calls ChatGroq and returns a response
- Maintains conversation history in state across turns

### Key files
- `state/chatbot_state.py` — defines `ChatState` (TypedDict with messages list)
- `nodes/chatbot_node.py` — single node, calls LLM, returns updated messages
- `graph/graph_builder.py` — StateGraph with chatbot node + edges
- `llms/llm_factory.py` — initialises `ChatGroq`
- `streamlitui/app.py` — Streamlit chat interface
- `main.py` — loads env, builds graph, runs UI

### Architecture

```
User input (Streamlit)
        │
        ▼
  ChatState (TypedDict)
  { messages: [...] }
        │
        ▼
  chatbot_node
  (ChatGroq LLM)
        │
        ▼
  Updated state
  { messages: [..., AIMessage] }
        │
        ▼
  Response displayed in Streamlit
```

---

## Phase 2 — 3-Layer Logging

### What it does
Adds three independent observability layers that run on every node execution:

| Layer | Tool | What it captures |
|-------|------|-----------------|
| Layer 1 | Custom JSON logger (`utils/logger.py`) | Node entry, exit, errors, confidence scores — written to `logs/chatbot.log` |
| Layer 2 | LangSmith tracing | Full chain traces, token usage, latency — visible in LangSmith dashboard |
| Layer 3 | `BaseCallbackHandler` | Node-level hooks: `on_llm_start`, `on_llm_end`, `on_tool_start`, `on_tool_end` |

### Key files
- `utils/logger.py` — `JSONFormatter` + `get_logger()` factory
- `nodes/chatbot_node.py` — updated to log input state, output, errors
- `graph/graph_builder.py` — `LoggerCallback` (BaseCallbackHandler) attached to graph
- `.env` — `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`

### Log format (Layer 1)
```json
{
  "timestamp": "2025-03-18T10:23:45.123Z",
  "level": "INFO",
  "node": "chatbot_node",
  "event": "node_exit",
  "input_messages": 3,
  "output": "The capital of France is Paris.",
  "latency_ms": 842
}
```

### Environment variables needed
```env
GROQ_API_KEY=your_groq_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=CHATBOT
```

---

## Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/MohamedArshadGit/MultiAgent-LLM-Agent-Orchestrator_lab.git
cd MultiAgent-LLM-Agent-Orchestrator_lab/CHATBOT

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment setup

```bash
cp .env.example .env
# Fill in your API keys in .env
```

`.env.example`:
```env
# LLM
GROQ_API_KEY=

# Observability
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=CHATBOT

# Phase 3 — Tools (add when starting Phase 3)
TAVILY_API_KEY=
OPENWEATHER_API_KEY=
NEWS_API_KEY=
```

### Run

```bash
# Run Streamlit UI
streamlit run streamlitui/app.py

# Or run via main.py
python main.py
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | ChatGroq (llama3-70b-8192) |
| Agent framework | LangGraph |
| LLM toolkit | LangChain |
| UI | Streamlit |
| Observability | LangSmith + custom JSON logger |
| Language | Python 3.11+ |
| **Coming — Phase 3** | |
| Tool protocol | MCP (FastMCP) |
| Web search | Tavily |
| Weather | OpenWeatherMap |
| News | NewsAPI |
| **Coming — Phase 6** | |
| Memory | Redis + RedisChatMessageHistory |
| **Coming — Phase 7** | |
| Vector DB | Pinecone / Chroma |
| Embeddings | HuggingFace / OpenAI |
| **Coming — Phase 8** | |
| Graph DB | Neo4j (community) + NetworkX |
| **Coming — Phase 9** | |
| Evaluation | DeepEval + RAGAS |
| **Coming — Phase 10** | |
| Containerisation | Docker + Kubernetes |
| CI/CD | GitHub Actions |
| Cloud | AWS Bedrock / Azure |

---

## Design Principles

### Modular structure
Every component is isolated. Adding a new phase never breaks existing phases — it only adds new files or extends existing ones.

### MCP-first tooling (Phase 3+)
All tools are exposed as MCP servers using `FastMCP`. This means:
- Tools are reusable across any agent, not just this chatbot
- Any MCP-compatible client (Claude, other LangGraph agents) can use the same tools
- Clean separation between tool logic and agent logic

### Logging standard
Every node logs three things:
1. Input state received
2. Output state returned
3. Any errors with full traceback

### Testing standard (Phase 9)
- **DeepEval** — unit tests every node for LLM output quality, hallucination, correctness
- **RAGAS** — RAG pipeline metrics: faithfulness, answer relevancy, context precision, context recall
- Every phase adds tests to `tests/` folder

---

## Roadmap Detail

### Phase 3 — Tools + ReAct agent
**New files:**
```
mcp_servers/
  tools_server.py      # calculator, datetime, location (no key)
  search_server.py     # Tavily web search
  weather_server.py    # OpenWeatherMap
  news_server.py       # NewsAPI
nodes/
  agent_node.py        # ReAct agent node — connects to MCP, binds tools to LLM
  tool_node.py         # Executes tool calls returned by LLM
graph/
  graph_builder.py     # Updated — adds tool loop + conditional edge
```

**How it works:**
- LLM receives user message + list of available tools
- LLM decides: call no tools / call one tool / call many tools in parallel
- `ToolNode` executes all tool calls simultaneously
- Results returned to LLM for final answer
- Loop repeats until LLM decides it has enough information

### Phase 4 — Router + Human-in-the-loop
- Router node classifies user intent → routes to right sub-graph
- HITL: graph pauses before sensitive actions, user confirms or cancels
- Uses LangGraph `interrupt()` for pause/resume

### Phase 5 — Orchestrator-worker
- Planner LLM breaks complex task into subtasks
- Worker agents run in parallel (each a compiled sub-graph)
- Orchestrator collects results and synthesises final answer
- Evolves into A2A pattern (each worker as FastAPI server)

### Phase 6 — Redis memory
- Username entered in Streamlit sidebar → becomes `session_id`
- `RedisChatMessageHistory` stores conversation per user
- History persists across app restarts
- All workflows share same memory layer

### Phase 7 — RAG + Corrective RAG + Adaptive RAG
- **Standard RAG** — ingest documents → embed → store in Pinecone → retrieve on query
- **Corrective RAG** — grade retrieved docs for relevance → re-retrieve or web-search if poor
- **Adaptive RAG** — route by complexity: simple → direct LLM, medium → RAG, complex → agent loop

### Phase 8 — GraphRAG
- Extract entities and relationships from documents
- Store in NetworkX (dev) → Neo4j (production)
- Hybrid retrieval: graph traversal + vector similarity
- Combined with standard RAG pipeline

### Phase 9 — DeepEval + RAGAS evaluation
- Node-level unit tests with DeepEval (hallucination, correctness, relevancy)
- RAG pipeline metrics with RAGAS (faithfulness, context precision, context recall)
- Ground truth dataset of synthetic test cases
- CI/CD integration — tests run on every push

### Phase 10 — Docker + K8s + CI/CD + Cloud
- Dockerfile + docker-compose for local
- Kubernetes manifests + Helm charts for production
- GitHub Actions pipeline: test → build → push → deploy
- AWS Bedrock or Azure OpenAI for cloud LLM
- AWS HealthLake / Azure Health Data Services for pharma compliance

---

## API Keys — Where to Get Them

| Key | URL | Free tier |
|-----|-----|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | ✅ Free |
| `LANGCHAIN_API_KEY` | [smith.langchain.com](https://smith.langchain.com) | ✅ Free tier |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | ✅ 1000/month |
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) | ✅ 1000/day |
| `NEWS_API_KEY` | [newsapi.org/register](https://newsapi.org/register) | ✅ 100/day dev |

---

## Author

**Mohamed Arshad**
AI Engineer — Crawley, UK
[github.com/MohamedArshadGit](https://github.com/MohamedArshadGit)

---

## Related Projects

- [`RAG_Lab`](https://github.com/MohamedArshadGit/RAG_Lab) — RAG pipeline experiments
- [`MultiAgent-LLM-Agent-Orchestrator_lab`](https://github.com/MohamedArshadGit/MultiAgent-LLM-Agent-Orchestrator_lab) — Multi-agent orchestration patterns

---

*This project is built phase by phase as a daily practice and portfolio centrepiece. Each phase is a self-contained, production-grade addition — not a throwaway prototype.*
