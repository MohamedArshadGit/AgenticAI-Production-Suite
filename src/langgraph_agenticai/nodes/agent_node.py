from langchain_core.messages import SystemMessage,AIMessage,HumanMessage
from langgraph_agenticai.state.state import State
from langgraph_agenticai.utils.logger import logger,callback_handler
import json

from pydantic import BaseModel,Field
from typing import Literal

#ambiguity result(pattern 6) Schema
class AmbiguityResult(BaseModel):
     """Schema for ambiguity detection response"""
     status:Literal["AMBIGUOUS", "CLEAR"]=Field(
        description="Whether the message is ambiguous or clear")
     option: list[str]=Field(
        default=[],
        description="Exactly 3 interpretations if AMBIGUOUS, empty list if CLEAR",
        min_length=0,
        max_length=3
     )


class Agentnode:
    def __init__(self,model,tools):
        """
        model : LLM (ChatGroq)
        tools : list of all 7 @tool functions
        """
        
        self.model=model
        self.model_with_tools=model.bind_tools(tools) # bind_tools tells LLM about available tools

        # ── structured output models ──────────────────────
        # SEPARATE model instances just for structured checks
        self.ambiguity_checker = model.with_structured_output(AmbiguityResult)

    def process(self,state:State)->dict:
        """
        Receives current state
        Passes messages to LLM
        LLM decides to reply or call a tool
        Returns updated messages + HITL fields if needed
        """
        # Recursion Guard (count how many tool calls have happened so far)
        # counts AIMessages with tool_calls in full history
        # e.g. if LLM looped 10 times requesting tools → something is wrong
        # tool_call_count = how many times agent looped back to call tools. Not how many tools. 4 tools in one shot = count of 1. Only hits 10 if something is seriously broken.
        tool_call_count = sum(
            1 for m in state["messages"]
            if hasattr(m, "tool_calls") and m.tool_calls # hasattr → safe check, if HumanMessage/ToolMessage don't have tool_calls it wont crash
        )

        # safety guard — LLM stuck in tool loop → force stop and reply safely
        if tool_call_count >= 10:
            logger.warning("AgentNode", "Max tool calls reached, forcing stop")
        
            return {"messages": [AIMessage(content="I was unable to complete the task after multiple attempts.")]}

        logger.info("AgentNode", "AgentNode started",
                        {"messages_count": len(state["messages"])})
        
        # — ambiguity check FIRST 
        ambiguity_result =self._check_ambiguity(state)
        if ambiguity_result:
            logger.info("AgentNode", "Ambiguity detected — HITL triggered")
            return ambiguity_result

        system_prompt = SystemMessage(content="""
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

            if getattr(response, "tool_calls", None): #instead of if response.tools(unsafe)
                # sensitive tool check
                sensitive = self._check_sensitive_tools(response)
                if sensitive:
                    logger.info("AgentNode", "Sensitive tools detected — HITL triggered",
                                {"tools": sensitive})
                    return {
                        "messages":[response], #That response object contains the LLM's decision to call the tool or not and what user rejects the tool use or not details etc
                        "hitl_required"   : True,
                        "hitl_pattern"    : "sensitive_tool",
                        "hitl_approved"   : None,
                        "hitl_message"    : f"Agent wants to use sensitive tools: {', '.join(sensitive)}. Allow?",
                        "sensitive_tools" : sensitive,
                        #"confidence_score": None,
                        "hitl_options"    : None
                    }


                logger.info("AgentNode", "LLM decided to call tools",
                            {"tools": [t["name"] for t in response.tool_calls]})
            else:
                logger.info("AgentNode", "LLM replied directly without tools")
                
        except Exception as e:
            logger.error("AgentNode", "LLM call failed", {"error": str(e)})
            raise

        logger.info("AgentNode", "AgentNode finished")
        return {"messages":[response]} # Why [response] in a list? LangGraph APPENDS response to existing messages and add_messages expects a list

    #Sensitive Tool Detection method
    def _check_sensitive_tools(self,response)->list:
        """
        Returns list of sensitive tools LLM wants to call
        Empty list = no sensitive tools

        """
        sensitive_tool_names = ["search_tool", "location_tool"]
        requested_tools =[t['name'] for t in response.tool_calls]
        return [t for t in requested_tools if t in sensitive_tool_names] #return sensitive tool only if is it in requested tools

    #check ambiguity method
    def _check_ambiguity(self,state:State)-> dict|None:
        """
        Checks if last user message is ambiguous
        Uses lightweight LLM call with strict prompt
        Returns HITL dict if ambiguous, else None
        """
        last_human =None
        for m in reversed(state['messages']): #reversed() loops messages backwards (latest first).
            if isinstance(m,HumanMessage): # isinstance always returns either True or False. Nothing else.y needed? to skip AI/Tool/System msgs, only want Humanmessage and to check if true continue or else skip
                last_human=m.content
                break
    
        if not last_human:
            return None
        
        # short messages are likely ambiguous
        # long detailed messages are likely clear
        if len(last_human.split())>6:
            return None  #skip check for long messages — likely clear

        try:
            #ask llm if message is ambiguos
            result: AmbiguityResult = self.ambiguity_checker.invoke([ # result: Ambi.. is called type hint. It is just a label for YOU and your code editor. It does NOT change how the code runs.
                    SystemMessage(content="""
                You are an ambiguity detector.
                    Decide if the user message is AMBIGUOUS or CLEAR.
                    AMBIGUOUS = multiple possible interpretations exist.
                    CLEAR     = only one obvious interpretation.
                    If AMBIGUOUS, provide exactly 3 distinct interpretations in 'options'.
                    If CLEAR, leave 'options' as an empty list.
                """),HumanMessage(content=f'User_Message:{last_human}')]
            )
        except Exception as e:
            logger.error("AgentNode", "Structured ambiguity check failed, skipping", {"error": str(e)})
            return None  # fail safe — don't block the user
        
        if result.status =='AMBIGUOUS' and len(result.option)>=2:
            logger.info("AgentNode", "Ambiguity detected", {"options": result.option})
            return {
                "messages"        : [],
                "hitl_required"   : True,
                "hitl_pattern"    : "ambiguity",
                "hitl_approved"   : None,
                "hitl_message"    : "Your message could mean multiple things. Please select:",
                "hitl_options"    : result.option,
                #"confidence_score": None,
                "sensitive_tools" : None

            }
        return None
        # y "messages": [], is empty here
        # User said:  "fix it"       ← ambiguous, short message
        # Pattern 6 runs BEFORE LLM is even called
        # LLM has not done anything yet
        # There is no response object

# Explanation for tool count       
# "weather in my location + iran news + 10+10 + read file"
# LLM calls all 4 tools in one shot — that is 1 AIMessage:
# AIMessage → tool_calls: [weather, search, calculator, file]  ← count = 1
# All 4 tools run, come back, LLM gives final answer. Done. Count never reaches 10.

# When would count increase?
# Only if LLM keeps looping — calling tools again and again:
# AIMessage → tool_calls: [weather, search, calculator, file]  ← count = 1
# AIMessage → tool_calls: [weather, search, calculator, file]  ← count = 2
# AIMessage → tool_calls: [weather, search, calculator, file]  ← count = 3
# ... something is broken, LLM stuck in loop ...
# AIMessage → tool_calls: [weather, search, calculator, file]  ← count = 10
# → STOP