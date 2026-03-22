from langchain_core.messages import SystemMessage
from src.langgraph_agenticai.state.state import State
from src.langgraph_agenticai.utils.logger import logger,callback_handler

class Agentnode:
    def __init__(self,model,tools):
        """
        model : LLM (ChatGroq)
        tools : list of all 7 @tool functions
        """
        
        self.model=model
        self.model_with_tools=model.bind_tools(tools) # bind_tools tells LLM about available tools

    def process(self,state:State)->dict:
        """
        Receives current state
        Passes messages to LLM
        LLM decides to reply or call a tool
        Returns updated messages
        """
        logger.info("AgentNode", "AgentNode started",
                    {"messages_count": len(state["messages"])})

        system_prompt =SystemMessage(content="""
        You are a helpful AI assistant with access to the following tools:
        - datetime  : Get current date and time for any timezone
        - calculator: Solve any math expression
        - location  : Get user's current location
        - search    : Search the web for latest information
        - weather   : Get weather for any city
        - file      : Read contents of a text file
        - currency  : Convert between currencies

        Use tools when needed. If you can answer directly, do so.
        Always give clear and helpful responses.
        """)
        messages =[system_prompt] + state['messages']
        try:
            response =self.model_with_tools.invoke(messages,
            config={"callbacks": [callback_handler]} # LangGraphCallbackHandler(logs)
            )  
            if response.tool_calls:
                logger.info("AgentNode", "LLM decided to call tools",
                            {"tools": [t["name"] for t in response.tool_calls]})
            else:
                logger.info("AgentNode", "LLM replied directly without tools")
                
        except Exception as e:
            logger.error("AgentNode", "LLM call failed", {"error": str(e)})
            raise

        logger.info("AgentNode", "AgentNode finished")
        return {"messages":[response]} # Why [response] in a list? LangGraph APPENDS response to existing messages and add_messages expects a list

    
