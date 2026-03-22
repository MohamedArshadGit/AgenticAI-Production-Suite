from src.langgraph_agenticai.state.state import State
from langchain_core.messages import ToolMessage

class Toolnode:
    def __init__(self,tools:list) -> None:
        """
        tools: list of all 7 @tool functions

        We convert list to dict for easy lookup:
        {
            "calculator"       : calculator_function,
            "get_weather"      : weather_function,
            "get_datetime"     : datetime_function,
            ...
        }
        """
        self.tools_dict ={tool.name:tool  for tool in tools} #used dict comprehension not to loop each and every tool(originally was in list) like list comprehension this is dictionary comprehension (same but {key:value}) self.tools_dict = {"calculator": calculator,"....."}
        #where tool.name data has ? # each tool has a .name property (comes from @tool decorator by using from langchain_core.tools import tool in each tools)tool naming will be same as function name we kept ,this is done by ToolNode library automatically.

    def process(self,state:State)->dict:
        """
        Reads last message from state (AIMessage with tool_calls)
        Finds which tool to run
        Runs the tool
        Returns result as ToolMessage
        """
        last_message =state['messages'][-1] #last([-1]) has AIMessage from agent_node-> It contains tool_calls list ..so we are accessing that using this varible last_message

        results =[]

        for tool_call in last_message.tool_calls:
            tool_name =tool_call['name']# Get tool name LLM wants to call  e.g. "calculator"
            tool_args=tool_call['args']# Get arguments LLM wants to pass  e.g. {"expression": "10+10"}
            tool_id=tool_call['id'] # Get tool id — needed for ToolMessage e.g. "call_abc123"
            

            if tool_name in self.tools_dict:
                tool=self.tools_dict[tool_name] # get the @tool function
                result =tool.invoke(tool_args) # run it with args
            else:
                result =f'Error: Tool {tool_name} not found'
            
            results.append(ToolMessage(content=str(result),
            tool_call_id=tool_id))## Wrap result in ToolMessage
            # ToolMessage tells LangGraph this is a tool result
            # Why `tool_call_id`?
            # LLM made tool call with id "call_abc123"
            # Tool ran and got result
            # ToolMessage says "this result belongs to call_abc123"
            # LLM can now match result to its original request

        return {"messages":results} # Return all tool results — LangGraph appends to state