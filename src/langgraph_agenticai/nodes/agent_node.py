from langchain_core.messages import SystemMessage
from langgraph_agenticai.state.state import State
from langgraph_agenticai.utils.logger import logger,callback_handler

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
        # count how many tool calls have happened so far
        tool_call_count = sum(
            1 for m in state["messages"]
            if hasattr(m, "tool_calls") and m.tool_calls
        )

        # if too many tool calls → force stop
        if tool_call_count >= 10:
            logger.warning("AgentNode", "Max tool calls reached, forcing stop")
            from langchain_core.messages import AIMessage
            return {"messages": [AIMessage(content="I was unable to complete the task after multiple attempts.")]}
            logger.info("AgentNode", "AgentNode started",
                        {"messages_count": len(state["messages"])})

        system_prompt =system_prompt = SystemMessage(content="""
        You are a helpful AI assistant with access to the following tools:
        - datetime_tool           : Get current date and time for any timezone
        - calculator_tool         : Solve any math expression
        - location_tool           : Get user's current location
        - search_tool             : Search the web for latest information
        - weather_tool            : Get weather for any city
        - file_tool               : Read contents of a text file
        - currency_converter_tool : Convert between currencies

        Always use the EXACT tool names listed above when calling tools.

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

    
