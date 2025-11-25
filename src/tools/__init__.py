"""
MAF-Compliant Tools

This module provides utility tools using MAF's native @ai_function
decorator pattern with Pydantic input validation.

All tools follow MAF SDK standards for type safety and schema generation.
"""

try:
    from agent_framework import ai_function
except ImportError:  # pragma: no cover
    def ai_function(func):
        """Fallback decorator when agent_framework is unavailable."""
        return func
try:
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    class BaseModel:  # minimal stub
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    def Field(*_, **__):
        """Fallback Field function when pydantic is unavailable."""
        return None
try:
    from ddgs import DDGS
except ImportError:  # pragma: no cover
    class DDGS:  # minimal stub
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def text(self, query, max_results=5):
            return []

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


# ============================================================================
# Input Models (Pydantic)
# ============================================================================

class SearchWebInput(BaseModel):
    """Input schema for web search tool."""
    query: str = Field(
        description="The search query to find information on the web"
    )


class AddContextInput(BaseModel):
    """Input schema for adding context."""
    key: str = Field(description="The key to store the value under")
    value: str = Field(description="The value to store")


class GetContextInput(BaseModel):
    """Input schema for retrieving context."""
    key: str = Field(description="The key to retrieve")


# ============================================================================
# Context Storage (Singleton Pattern)
# ============================================================================

_context_store: dict[str, str] = {}


# ============================================================================
# MAF AIFunctions (Tools)
# ============================================================================

@ai_function
def search_web(input: SearchWebInput) -> str:
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
            results = list(ddgs.text(input.query, max_results=5))
        
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


@ai_function
def add_context(input: AddContextInput) -> str:
    """
    Stores a key-value pair in persistent context for later retrieval.
    
    Use this to remember important information across the conversation.
    """
    _context_store[input.key] = input.value
    return f"Stored: '{input.key}' = '{input.value}'"


@ai_function
def get_context(input: GetContextInput) -> str:
    """
    Retrieves a value from persistent context.
    
    Use this to recall information that was previously stored.
    """
    value = _context_store.get(input.key)
    if value is None:
        return f"No context found for key: '{input.key}'"
    return value


@ai_function
def clear_context() -> str:
    """
    Clears all stored context.
    
    Use this to reset the agent's memory when starting a new topic.
    
    Note: This tool takes no input parameters.
    """
    count = len(_context_store)
    _context_store.clear()
    return f"Context cleared. Removed {count} items."


# ============================================================================
# Tool Exports
# ============================================================================

# List of all utility tools for agent registration
ALL_UTILITY_TOOLS = [
    search_web,
    add_context,
    get_context,
    clear_context
]

# Combined exports from tier-organized tool modules
try:
    from src.tools.tier4 import ALL_TIER4_TOOLS
    from src.tools.tier2 import ALL_TIER2_TOOLS
    from src.tools.tier2.validation_tool import ValidationTool
    
    # For backward compatibility, expose ALL_CODE_TOOLS
    from src.tools.tier4.code_tools import ALL_CODE_TOOLS
    
    ALL_TOOLS = ALL_TIER4_TOOLS + ALL_TIER2_TOOLS + ALL_UTILITY_TOOLS + [ValidationTool]
except ImportError as e:
    # Fallback if tier imports fail
    ALL_CODE_TOOLS = []
    ALL_TOOLS = ALL_UTILITY_TOOLS

