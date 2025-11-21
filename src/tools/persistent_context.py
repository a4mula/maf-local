"""
MAF-native persistent context tools for stateful agent memory.
"""

from typing import Annotated
from pydantic import Field

# Shared context storage (singleton pattern)
_context_store: dict[str, str] = {}


def add_context(
    key: Annotated[str, Field(description="The key to store the value under")],
    value: Annotated[str, Field(description="The value to store")]
) -> str:
    """
    Stores a key-value pair in persistent context for later retrieval.
    
    Use this to remember important information across the conversation,
    such as user preferences, facts, or intermediate results.
    
    Args:
        key: The identifier for this piece of information
        value: The information to remember
        
    Returns:
        Confirmation message
    """
    _context_store[key] = value
    return f"Stored: '{key}' = '{value}'"


def get_context(
    key: Annotated[str, Field(description="The key to retrieve")]
) -> str:
    """
    Retrieves a value from persistent context.
    
    Use this to recall information that was previously stored.
    
    Args:
        key: The identifier for the information to retrieve
        
    Returns:
        The stored value, or a message if not found
    """
    value = _context_store.get(key)
    if value is None:
        return f"No context found for key: '{key}'"
    return value


def clear_context() -> str:
    """
    Clears all stored context.
    
    Use this to reset the agent's memory when starting a new topic
    or when the user requests it.
    
    Returns:
        Confirmation message with count of cleared items
    """
    count = len(_context_store)
    _context_store.clear()
    return f"Context cleared. Removed {count} items."
