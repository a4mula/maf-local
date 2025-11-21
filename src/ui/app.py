import chainlit as cl
import asyncio
from src.services.agent_factory import AgentFactory
from src.agents.core_agent import CoreAgent

@cl.on_chat_start
async def start():
    """
    Initializes the agent and message bus when a new chat session starts.
    """
    # Define a callback to update the UI when the agent performs a step
    async def on_step(name, type, args):
        async with cl.Step(name=name, type=type) as step:
            step.input = args
            step.output = "Executing..."
            # We could update this with the result if we refactored CoreAgent to pass it back
            # For now, just showing the call is a huge win.

    # Create the agent using the factory
    # We need to inject the on_step callback. 
    # Since AgentFactory doesn't support it yet, we might need to monkey-patch or update factory.
    # For simplicity, let's construct manually or update factory later.
    # Actually, let's just use the factory and then attach the callback if possible, 
    # but CoreAgent takes it in __init__.
    # Let's update the factory to accept kwargs for agent init? 
    # Or just instantiate manually here to be safe and fast.
    
    from src.clients.litellm_client import LiteLLMChatClient
    from src.persistence.audit_log import AuditLogProvider
    from src.persistence.message_store import MessageStoreProvider
    from src.config.tool_registry import TOOL_REGISTRY
    from src.middleware.message_bus import MessageBus
    
    # Initialize dependencies
    client = LiteLLMChatClient(model_name="ollama/llama3.1:8b")
    audit_log = AuditLogProvider()
    message_store = MessageStoreProvider(session_id=cl.user_session.get("id"))
    
    # Initialize Agent with Callback
    agent = CoreAgent(
        name="Local-Dev-Agent",
        system_prompt="You are a helpful AI assistant running locally.",
        client=client,
        audit_log=audit_log,
        message_store=message_store,
        registered_tools=TOOL_REGISTRY["Local-Dev"],
        on_step=on_step
    )
    
    # Initialize Bus
    bus = MessageBus()
    agent.connect_bus(bus)
    
    # Store agent in session
    cl.user_session.set("agent", agent)
    
    await cl.Message(content="**System:** Agent Ready! I am connected to the Message Bus and have access to Web Search.").send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming user messages.
    """
    agent: CoreAgent = cl.user_session.get("agent")
    
    # Create a root step for the "Thinking" process
    async with cl.Step(name="Agent Loop", type="run") as step:
        step.input = message.content
        
        # Run the agent
        response = await agent.process(message.content)
        
        step.output = response

    # Send the final answer
    await cl.Message(content=response).send()
