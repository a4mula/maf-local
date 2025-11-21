"""
MAF-native communication tools for agent-to-agent messaging.
"""

from typing import Annotated, Optional
from pydantic import Field

# This will be injected by CoreAgent when needed
_message_bus: Optional[any] = None


def send_message(
    recipient: Annotated[str, Field(description="The name of the agent to send the message to")],
    content: Annotated[str, Field(description="The message content to send")]
) -> str:
    """
    Sends a message to another agent for collaboration.
    
    Use this when you need help from a specialized agent or want to
    delegate a task to another agent in the system.
    
    Args:
        recipient: The name/ID of the target agent
        content: The message to send
        
    Returns:
        Confirmation message
    """
    if _message_bus is None:
        return "Message bus not available. Agent-to-agent communication is disabled."
    
    try:
        # This would use the message bus to send
        # For now, return a placeholder
        return f"Message sent to {recipient}: {content}"
    except Exception as e:
        return f"Failed to send message: {str(e)}"


def set_message_bus(bus):
    """Internal function to inject message bus dependency."""
    global _message_bus
    _message_bus = bus
