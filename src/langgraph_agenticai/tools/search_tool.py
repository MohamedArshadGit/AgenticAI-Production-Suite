from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

def search_web(query:str,max_results:int=5)->dict:
    """
    Search the web for current and up to date information using Tavily.
    Use this when the user asks about recent events, news, current affairs,
    latest updates, or anything that requires live internet information.
    Examples: 'Who won the Champions League?', 'Latest AI news',
    'Current LangGraph version', 'What happened today in UK?'

    Args:
        query      : The search query string
        max_results: Number of results to return (default 5)

    Returns:
        dict with search results including titles, urls and content
    """

    try:
        api_key =os.getenv('TAVILY_API_KEY')
        if not api_key:
            return{"status":"Error",
                   "message":"TAVILY_API_KEY not found in environment variable"}
        
        client =TavilyClient(api_key)
        # perform the search
        # search_depth "basic" = faster, "advanced" = more thorough
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )

        results =response.get('results',[]) # return [] if no results ..but without [] also it wont crash because .get return None as default if results not there

        if not results: # what not result means ? results = []# empty list ,results = None # None ,results = "" # empty string  results = 0 # zero  
            return{
                "status": "success",
                "message": "No results found for this query.",
                "results": []
            }
        #format each result cleanly
        formatted_results=[]
        for result in results:
            formatted_results.append({
                "title":result.get('title'),
                "url":result.get('url'),
                "content": result.get("content"),
                "score": result.get("score")  # relevance score 0-1
            })
        
        return{
            "status":"success",
            "query":query,
            "total_results":len(formatted_results),
            "results":formatted_results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
