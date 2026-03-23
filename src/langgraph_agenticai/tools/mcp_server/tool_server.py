import sys
import os
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')
    )
)

from langgraph_agenticai.tools.calculator_tool import calculator
from langgraph_agenticai.tools.currency_tool import currency_converter
from langgraph_agenticai.tools.datetime_tool import get_datetime
from langgraph_agenticai.tools.file_tool import file_reader_tool
from langgraph_agenticai.tools.location_tool import get_location
from langgraph_agenticai.tools.search_tool import search_web
from langgraph_agenticai.tools.weather_tool import get_weather

from mcp.server.fastmcp import FastMCP
import sys
import os

#Create mcp Server instance with a name
mcp =FastMCP(name='Chatbot-tool-server')

#Register all 7 tools with mcp Server

@mcp.tool() #This decorator registers function as MCP tool
def calculator_tool(expression:str)->str:
    """
    Evaluate a mathematical expression safely.
    Use this for any arithmetic, algebra, or mathematical calculations.
    Examples: '10 + 10', 'sqrt(16)', '2**8', 'sin(90)', '100 * 0.18'
    """
    return calculator.invoke({"expression":expression})

@mcp.tool()
def currency_converter_tool(amount:float,from_currency:str,to_currency:str)->str:
    """
    Convert an amount from one currency to another using live exchange rates.
    Use this when user asks about currency conversion or exchange rates.
    """
    return currency_converter.invoke({
        "amount":amount,
        "from_currency":from_currency,
        "to_currency":to_currency
    })

@mcp.tool()
def datetime_tool(timezone :str='UTC')->str:
    """
    Get the current date and time for a given timezone.
    Use this when user asks about current time, date, or day of the week.
    Timezone string e.g. 'UTC', 'Europe/London', 'Asia/Kolkata'.
    """
    return get_datetime.invoke({"timezone":timezone})

@mcp.tool()
def file_tool(file_path:str)->str:
    """
    Reads and returns the contents of a text file from the given file path.
    Use this when user wants to read or view contents of a file.
    """
    return file_reader_tool.invoke({"file_path":file_path})

@mcp.tool()
def location_tool()->str:
    """
    Get the current location of the user based on their IP address.
    Use this when user asks about their current location.

    """
    return get_location.invoke({})

@mcp.tool()
def search_tool(query: str, max_results: int)->str:
    """
    Search the web for current and up to date information using Tavily.
    Use this when user asks about recent events, news, or current affairs.
    """
    return search_web.invoke({"query":query,"max_results":max_results})

@mcp.tool()
def weather_tool(city: str = None, latitude: float = None, longitude: float = None):
    """
    Get current weather conditions for a city or coordinates.
    Use this when user asks about weather, temperature, or forecast.
    """
    return get_weather.invoke({"city":city, "latitude":latitude, "longitude":longitude})

if __name__=="__main__":
    print("Starting MCP tools Server")
    print("All 7 tools registered and ready.")
    mcp.run(transport="streamable-http") 