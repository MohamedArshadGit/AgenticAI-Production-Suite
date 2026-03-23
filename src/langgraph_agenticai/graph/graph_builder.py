from langgraph_agenticai.state.state import State
from langgraph_agenticai.nodes.basic_chatbot_node import BasicChatbotNode

from langgraph.graph import StateGraph,START,END
from langchain_core.messages import AIMessage

from langgraph_agenticai.nodes.agent_node import Agentnode
from langgraph_agenticai.nodes.tool_node import Toolnode
from langgraph_agenticai.utils.logger import logger, callback_handler

class GraphBuilder:
    def __init__(self,model):
        self.llm =model
        # self.llm = ChatGroq object received from main.py
        self.graph_builder =StateGraph(State)
        # creates empty graph that uses State as data format

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node = BasicChatbotNode(self.llm) #is this object here self.basic_chatbot_node
        #    ↑                     ↑
        #    this is the object     this is the class
        self.graph_builder.add_node('chatbot',self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,'chatbot') 
        self.graph_builder.add_edge('chatbot',END)
        return self.graph_builder.compile()   # return compiled graph
    
    def setup_graph(self, usecase: str, tools: list = None):
    #                                   ^^^^^^^^^^^^^^^^^^
    #                                   tools from MCP server passed in from app.py
        """
        usecase = "Basic Chatbot" or "Tools + ReAct"
        tools   = list from MCP server (only for Tools+ReAct)
        """
        if usecase == "Basic Chatbot":
            return self.basic_chatbot_build_graph()

        elif usecase == "Tools + ReAct":
            if not tools:
                logger.error("GraphBuilder", "No tools provided for Tools+ReAct")
                raise ValueError("Tools list is empty. MCP server may not be running.")
            return self.tools_chatbot_build_graph(tools)
    
    # Phase 3 — Tools + ReAct
    def tools_chatbot_build_graph(self,tools:list):
        """
        Builds a ReAct agent graph with 7 tools.

        Graph flow:
        START → agent_node → tool_node (if tool call)
                           → END       (if direct reply)
                ↑               |
                └───────────────┘
                (loop back after tool runs)
        """

        #create nodes
        self.agent_node =Agentnode(self.llm,tools)
        self.tool_node =Toolnode(tools)

        #add nodes
        self.graph_builder.add_node('agent',self.agent_node.process)
        self.graph_builder.add_node('tools',self.tool_node.process)

        #add edges
        self.graph_builder.add_edge(START,'agent')
        self.graph_builder.add_conditional_edges(
            "agent",               # FROM this node
            self.should_use_tool,  # CALL this function
            {
                "tools": "tools",  # if returns "tools" → go to tools node
                "end"  : END       # if returns "end"   → go to END
            }
        )
        self.graph_builder.add_edge('tools','agent')

        logger.info("GraphBuilder", "Tools+ReAct graph built",
                    {"tools_count": len(tools)})

        return self.graph_builder.compile()

        
    def should_use_tool(self, state: State) -> str:

        """
        If LLM made tool calls → route to tools node
        If LLM replied directly → route to END
        """
        last_message = state["messages"][-1]

        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            logger.info("GraphBuilder", "Routing to tools",
                        {"tools": [t["name"] for t in last_message.tool_calls]})
            return "tools"

        logger.info("GraphBuilder", "Routing to END")
        return "end"
        # after agent runs → call should_use_tool() → it returns a string
        # that string decides where to go next
        # ```
        # "tools" → matched to "tools": "tools" in dict → goes to tools node
        # "end"   → matched to "end": END in dict       → goes to END


