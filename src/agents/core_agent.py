import io
import contextlib
from typing import List, Dict, Any

from src.clients.base import IChatClient
from src.persistence.audit_log import AuditLogProvider # New Import
from src.persistence.message_store import MessageStoreProvider # New Import

class CoreAgent:
    """
    The Unified Agent.
    It does not know *which* model it is using, only that it has an IChatClient.
    It now accepts and utilizes persistence providers via Dependency Injection.
    """
    def __init__(
        self, 
        name: str, 
        system_prompt: str,  # <-- KEEP: Original parameter for DI compliance
        client: IChatClient,
        audit_log: AuditLogProvider,     # New Dependency: Audit Log Provider
        message_store: MessageStoreProvider # New Dependency: Message Store Provider
    ):
        self.name = name
        # self.system_prompt = system_prompt  # <-- COMMENTED OUT: Original code for DI
        self.client = client # The injected LLM client
        self.audit_log = audit_log # The injected audit provider
        self.message_store = message_store # The injected message store
        
        # 🛑 TEMPORARY DI VIOLATION FOR VALIDATION 🛑
        # JUSTIFICATION: We must load a strict system prompt here, overriding the injected one, 
        # to guarantee the fix for the LLM's final reasoning error (31.5 calculation).
        # This will be reverted after validation is complete.
        self.system_prompt = (
            "You are a helpful and precise AI assistant running locally on an RTX 3060 Ti. "
            "Your main goal is accuracy. When a tool returns a result, you MUST prioritize "
            "that exact, verbatim result and integrate it accurately into your final answer. "
            "Do not perform any additional mathematical reasoning or recalculation."
        )

        # HISTORY INITIALIZATION: 
        # Starts with the system prompt. In a production app, the history
        # would be asynchronously loaded from message_store here.
        self.history: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        # Note: self.history now uses the hardcoded self.system_prompt
        
    async def process(self, user_input: str) -> str:
        # 1. Log Process Start
        await self.audit_log.log(
            agent_name=self.name,
            operation="PROCESS_START",
            details=f"Received input: {user_input[:50]}..."
        )
        
        # 2. Update Memory & Store User Message
        user_message = {"role": "user", "content": user_input}
        self.history.append(user_message)
        await self.message_store.store_message(user_message['role'], user_message['content']) # Store to DB

        # 3. Delegate to the Client (The "Brain")
        response_content = await self.client.chat(self.history)
        
        # 4. Update Memory & Store Agent Response
        agent_message = {"role": "assistant", "content": response_content}
        self.history.append(agent_message)
        await self.message_store.store_message(agent_message['role'], agent_message['content']) # Store to DB
        
        # 5. Log Process End
        await self.audit_log.log(
            agent_name=self.name,
            operation="PROCESS_END",
            details=f"Sent response: {response_content[:50]}..."
        )

        return response_content
