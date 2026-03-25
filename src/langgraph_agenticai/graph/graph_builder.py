from langgraph_agenticai.state.state import State
from langgraph_agenticai.nodes.basic_chatbot_node import BasicChatbotNode

from langgraph.graph import StateGraph,START,END
from langchain_core.messages import AIMessage

from langgraph_agenticai.nodes.agent_node import Agentnode
from langgraph_agenticai.nodes.tool_node import Toolnode
from langgraph_agenticai.nodes.hitl_node import HITLNode
from langgraph_agenticai.utils.logger import logger

from langgraph.checkpoint.memory import MemorySaver

class GraphBuilder:
    def __init__(self,model):
        self.llm =model
        # self.llm = ChatGroq object received from main.py
        self.graph_builder =StateGraph(State)
        # creates empty graph that uses State as data format

    
    
    def setup_graph(self, usecase: str, tools: list = None):
    #                                   ^^^^^^^^^^^^^^^^^^
    #                                   tools from MCP server passed in from app.py
        """
        usecase = "Basic Chatbot" or "Tools + ReAct" or "Tools + ReAct + HITL"
        tools   = list from MCP server (only for Tools + ReAct and Tools + ReAct + HITL )

        """
        if usecase == "Basic Chatbot":
            return self.basic_chatbot_build_graph()

        elif usecase == "Tools + ReAct":
            if not tools:
                logger.error("GraphBuilder", "No tools provided for Tools+ReAct")
                raise ValueError("Tools list is empty. MCP server may not be running.")
            return self.tools_chatbot_build_graph(tools)
        
        elif usecase == "Tools + ReAct + HITL":
            if not tools:
                logger.error("GraphBuilder", "No tools provided for Tools + ReAct + HITL")
                raise ValueError("Tools list is empty. MCP server may not be running.")
            return self.hitl_chatbot_build_graph(tools)

    
    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.graph_builder =StateGraph(State)
        self.basic_chatbot_node = BasicChatbotNode(self.llm) #is this object here self.basic_chatbot_node
        #    ↑                     ↑
        #    this is the object     this is the class
        self.graph_builder.add_node('chatbot',self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,'chatbot') 
        self.graph_builder.add_edge('chatbot',END)
        return self.graph_builder.compile()   # return compiled graph

    
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
        self.graph_builder =StateGraph(State)
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

    #phase 4 -> HITL + ReAct
    def hitl_chatbot_build_graph(self, tools: list):
        self.graph_builder =StateGraph(State)
        self.agent_node =Agentnode(self.llm,tools)
        self.tool_node=Toolnode(tools)
        self.hitl_node=HITLNode()

        #add nodes
        self.graph_builder.add_node('agent',self.agent_node.process)
        self.graph_builder.add_node('hitl',  self.hitl_node.process)
        self.graph_builder.add_node('tools', self.tool_node.process)

        #Add Edges
        self.graph_builder.add_edge(START,'agent')
        
        # agent → decide: needs HITL? needs tools? or done?
        self.graph_builder.add_conditional_edges(
            "agent",
            self.route_after_agent,
            {
                "hitl" : "hitl",
                "tools": "tools",
                "end"  : END
            }
        )

        # hitl → decide: approved? rejected? ambiguity selected?
        self.graph_builder.add_conditional_edges(
            "hitl",
            self.route_after_hitl,
            {
                "tools"  : "tools",  # approved sensitive tool
                "agent"  : "agent",  # ambiguity resolved → re-run agent
                "end"    : END       # rejected → stop
            }
        )

        # tools always loop back to agent for final answer
        self.graph_builder.add_edge('tools', 'agent')
        logger.info("GraphBuilder", "HITL graph built",
                    {"tools_count": len(tools)})

        # MemorySaver is required for interrupt_before to work
        # It checkpoints state so graph can resume after user input
        memory = MemorySaver()
        return self.graph_builder.compile(
            checkpointer=memory,
            interrupt_before=["hitl"]  # graph pauses BEFORE hitl node runs
        )

    def route_after_agent(self, state: State) -> str:
        """
        Called after agent_node runs.
        3 possible routes:
          hitl  → agent detected sensitive tool or ambiguity
          tools → agent wants tools, no HITL needed
          end   → agent replied directly, no tools
        """
        if state.get('hitl_required'):
            logger.info("GraphBuilder", "Routing to HITL",
                        {"pattern": state.get("hitl_pattern")})
            return 'hitl'
        
        last_message =state["messages"][-1] # last message contain Ai message and tool call details
        if isinstance(last_message, AIMessage) and last_message.tool_calls: # only runs if the LLM just spoke ,safe to check last_message.tool_calls here
            logger.info("GraphBuilder", "Routing to tools")
            return "tools"
        
        logger.info("GraphBuilder", "Routing to END")
        return "end"
    
    def route_after_hitl(self, state: State) -> str:
        """
        Called after hitl_node runs (after user made a decision in UI).
        3 possible routes:
          tools → sensitive tool approved → execute it
          agent → ambiguity resolved → re-run agent with clarified message
          end   → sensitive tool rejected → stop
        """
        pattern =state.get('hitl_pattern') #this we get from agent_node's process 'sensitive' or 'ambiguity'
        approved =state.get('hitl_approved') # this we will get from streamlit ui by user either user may reject or approve

        if pattern == "sensitive_tool":
            if approved:
                logger.info("GraphBuilder", "Sensitive tool approved → tools")
                return "tools"
            else:
                logger.info("GraphBuilder", "Sensitive tool rejected → end")
                return "end" #user reject access of tools
        
        if pattern == "ambiguity":
            # user selected one of the 3 options
            # agent_node will re-run with the clarified message
            logger.info("GraphBuilder", "Ambiguity resolved → agent")
            return "agent" 

        return 'end' # ← only reaches here if BOTH sensitive tool and ambuiguity above were skipped

        
        
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


