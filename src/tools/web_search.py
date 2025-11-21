"""
MAF-native web search tool using DuckDuckGo.
"""

from typing import Annotated
from pydantic import Field
from ddgs import DDGS


def search_web(
    query: Annotated[str, Field(description="The search query to find information on the web")]
) -> str:
    """
    Performs a web search using DuckDuckGo to find current information, news, or documentation.
    
    Use this tool when you need to:
    - Find current information not in your training data
    - Look up recent news or events
    - Search for technical documentation
    - Get real-time information
    
    Args:
        query: The search query string
        
    Returns:
        A formatted string with search results including titles, snippets, and URLs
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return "No results found."
        
        # Format results
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   {result.get('body', 'No description')}\n"
                f"   URL: {result.get('href', 'No URL')}"
            )
        
        return "\n\n".join(formatted)
        
    except Exception as e:
        return f"Search failed: {str(e)}"
