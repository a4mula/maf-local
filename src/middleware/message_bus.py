import asyncio
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from src.utils import get_logger

logger = get_logger(__name__)

@dataclass
class Message:
    """
    Standard Message schema for Agent-to-Agent communication.
    """
    sender: str
    recipient: str
    content: str
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MessageBus:
    """
    A local in-memory message bus for routing messages between agents.
    """
    def __init__(self):
        self._subscribers: Dict[str, Callable[[Message], Any]] = {}

    def register_agent(self, agent_name: str, callback: Callable[[Message], Any]):
        """
        Registers an agent's callback function to receive messages.
        """
        logger.info(f"[MessageBus] Registering agent: {agent_name}")
        self._subscribers[agent_name] = callback

    async def send(self, message: Message) -> bool:
        """
        Routes a message to the recipient.
        Returns True if delivered, False if recipient not found.
        """
        recipient = message.recipient
        if recipient in self._subscribers:
            logger.info(f"[MessageBus] Routing message from '{message.sender}' to '{recipient}'")
            # Execute the callback (can be sync or async, but we await if it's a coroutine)
            callback = self._subscribers[recipient]
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                callback(message)
            return True
        else:
            logger.info(f"[MessageBus] WARNING: Recipient '{recipient}' not found.")
            return False

    async def broadcast(self, sender: str, content: str):
        """
        Sends a message to all registered agents except the sender.
        """
        for agent_name in self._subscribers:
            if agent_name != sender:
                msg = Message(sender=sender, recipient=agent_name, content=content)
                await self.send(msg)
