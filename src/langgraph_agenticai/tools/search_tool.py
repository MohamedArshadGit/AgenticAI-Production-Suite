from tavily import TavilyClient
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
load_dotenv()

@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for current and up to date information using Tavily.
    Use this when the user asks about recent events, news, current affairs,
    latest updates, or anything that requires live internet information.
    Examples: 'Who won the Champions League?', 'Latest AI news',
    'Current LangGraph version', 'What happened today in UK?'
    """
    try:
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            return "Error: TAVILY_API_KEY not found in environment variables."

        client = TavilyClient(api_key)
        # perform the search
        # search_depth "basic" = faster, "advanced" = more thorough
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )

        results = response.get('results', []) # return [] if no results ..but without [] also it wont crash because .get return None as default if results not there

        if not results: # what not result means ? results = []# empty list ,results = None# None ,results = "" # empty string  results = 0 # zero
            return "No results found for this query."

        # format each result cleanly
        formatted = []
        for result in results:
            formatted.append(
                f"Title: {result.get('title')} | "
                f"URL: {result.get('url')} | "
                f"Content: {result.get('content')} | "
                f"Score: {result.get('score')}"  # relevance score 0-1
            )

        return (
            f"Query: {query}\n"
            f"Total Results: {len(formatted)}\n\n" +
            "\n\n".join(formatted)
        )

    except Exception as e:
        return f"Error: {str(e)}"