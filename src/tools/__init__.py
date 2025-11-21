"""
Tool Definitions - Register all tools with the universal registry
"""

from typing import Annotated
from pydantic import Field
from ddgs import DDGS

from src.tools.universal_tools import registry


@registry.register
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
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        
        if not results:
            return "No results found."
        
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


# Context storage (singleton pattern)
_context_store: dict[str, str] = {}


@registry.register
def add_context(
    key: Annotated[str, Field(description="The key to store the value under")],
    value: Annotated[str, Field(description="The value to store")]
) -> str:
    """
    Stores a key-value pair in persistent context for later retrieval.
    
    Use this to remember important information across the conversation.
    """
    _context_store[key] = value
    return f"Stored: '{key}' = '{value}'"


@registry.register
def get_context(
    key: Annotated[str, Field(description="The key to retrieve")]
) -> str:
    """
    Retrieves a value from persistent context.
    
    Use this to recall information that was previously stored.
    """
    value = _context_store.get(key)
    if value is None:
        return f"No context found for key: '{key}'"
    return value


@registry.register
def clear_context() -> str:
    """
    Clears all stored context.
    
    Use this to reset the agent's memory when starting a new topic.
    """
    count = len(_context_store)
    _context_store.clear()
    return f"Context cleared. Removed {count} items."
