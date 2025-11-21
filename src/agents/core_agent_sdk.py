"""
CoreAgent - MAF SDK-Native Agent with Tool Execution Loop

Implements the full tool execution cycle:
1. Receive FunctionCallContent from MAF
2. Execute tools using universal registry
3. Send FunctionResultContent back
4. Get final response
"""

from typing import Optional
from agent_framework import ChatAgent, AgentThread, FunctionResultContent, ChatMessage
import json

from src.adapters.maf_adapter import LiteLLMModelClient
from src.clients.litellm_client import LiteLLMChatClient
from src.persistence.audit_log import AuditLogProvider
from src.persistence.maf_message_store import PostgreSQLMessageStore
from src.config.settings import settings
from src.middleware.message_bus import MessageBus, Message

# Import tools to register them
import src.tools
from src.tools.universal_tools import registry


class CoreAgent:
    """
    MAF SDK-native Agent with full tool execution loop.
    """
    
    def __init__(
        self,
        client: LiteLLMChatClient,
        audit_log: AuditLogProvider,
        agent_type: str = "Local-Dev",
        on_step: Optional[callable] = None
    ):
        """
        Initialize CoreAgent with SDK ChatAgent.
        """
        self.client = client
        self.audit_log = audit_log
        self.agent_type = agent_type
        self.on_step = on_step
        self.bus: Optional[MessageBus] = None
        
        # Thread management
        self.threads: dict[str, AgentThread] = {}
        
        # Wrap LiteLLM client with SDK adapter
        sdk_client = LiteLLMModelClient(client=client)
        
        # Get tools in MAF format from universal registry
        maf_tools = registry.get_maf_tools()
        
        # Create SDK ChatAgent
        self.sdk_agent = ChatAgent(
            chat_client=sdk_client,
            name=agent_type,
            description=f"MAF Agent ({agent_type})",
            instructions=settings.AGENT_SYSTEM_PROMPT,
            tools=maf_tools,
            temperature=0.7,
            chat_message_store_factory=lambda: PostgreSQLMessageStore(
                session_id=f"{agent_type}_default"
            )
        )
    
    def get_or_create_thread(self, conversation_id: str) -> AgentThread:
        """Get existing thread or create a new one."""
        if conversation_id not in self.threads:
            message_store = PostgreSQLMessageStore(
                session_id=f"{self.agent_type}_{conversation_id}"
            )
            self.threads[conversation_id] = AgentThread(message_store=message_store)
        
        return self.threads[conversation_id]
    
    async def process(self, user_input: str, conversation_id: str = "default") -> str:
        """
        Process user input with full tool execution loop.
        
        Flow:
        1. Send user input to MAF
        2. If response contains tool calls, execute them
        3. Send results back to MAF
        4. Return final response
        """
        try:
            thread = self.get_or_create_thread(conversation_id)
            
            # Initial request
            response = await self.sdk_agent.run(user_input, thread=thread)
            
            # Check if response contains tool calls
            if response.messages and len(response.messages) > 0:
                msg = response.messages[0]
                
                # Check for FunctionCallContent
                if hasattr(msg, 'contents') and msg.contents:
                    from agent_framework import FunctionCallContent
                    
                    tool_calls = [c for c in msg.contents if isinstance(c, FunctionCallContent)]
                    
                    if tool_calls:
                        # Execute tools and collect results
                        tool_results = []
                        
                        for tool_call in tool_calls:
                            print(f"[Tool Execution] Calling: {tool_call.name}")
                            
                            # Parse arguments
                            try:
                                args = json.loads(tool_call.arguments)
                            except:
                                args = {}
                            
                            # Execute tool using universal registry
                            try:
                                result = await registry.execute_tool(tool_call.name, caller_role=self.agent_type, **args)
                                result_str = str(result)
                                print(f"[Tool Execution] Result: {result_str[:100]}...")
                            except Exception as e:
                                result_str = f"Error executing tool: {str(e)}"
                                print(f"[Tool Execution] Error: {e}")
                            
                            # Create FunctionResultContent
                            tool_results.append(
                                FunctionResultContent(
                                    call_id=tool_call.call_id,
                                    result=result_str
                                )
                            )
                        
                        # Send tool results back to MAF and get final response
                        final_response = await self.sdk_agent.run(
                            messages=[ChatMessage(role="tool", contents=tool_results)],
                            thread=thread
                        )
                        
                        return final_response.text
            
            # No tool calls, return text directly
            return response.text
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"
    
    def connect_bus(self, bus: MessageBus):
        """Connect to message bus for A2A communication."""
        self.bus = bus
        self.bus.register_agent(self.agent_type, self.receive_message)
    
    async def receive_message(self, message: Message):
        """Handle incoming messages from other agents."""
        pass
