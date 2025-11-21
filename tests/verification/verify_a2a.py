import asyncio
from src.middleware.message_bus import MessageBus
from src.agents.core_agent import CoreAgent
from src.tools.communication_tools import CommunicationTools

# Mock classes to avoid full agent initialization overhead
class MockAuditLog:
    async def log(self, *args): pass

class MockMessageStore:
    def __init__(self): self.session_id = "test-session"
    async def store_message(self, *args): pass
    async def get_history(self, *args): return []

class MockClient:
    async def chat(self, *args, **kwargs): return "Mock Response"

async def main():
    print("--- Verifying A2A Communication ---")
    
    # 1. Setup Bus
    bus = MessageBus()
    
    # 2. Setup Agents
    # We use real CoreAgent but with mock dependencies for speed
    agent_a = CoreAgent("Agent-A", "", MockClient(), MockAuditLog(), MockMessageStore(), [])
    agent_b = CoreAgent("Agent-B", "", MockClient(), MockAuditLog(), MockMessageStore(), [])
    
    # 3. Connect to Bus
    agent_a.connect_bus(bus)
    agent_b.connect_bus(bus)
    
    # 4. Test Sending Message (Simulating Tool Usage)
    # We manually instantiate the tool for Agent A to simulate it being loaded
    comm_tool_a = CommunicationTools(agent=agent_a)
    
    print("\n[Step 1] Agent A sending message to Agent B...")
    result = await comm_tool_a.send_message("Agent-B", "Hello from A!")
    print(f"Tool Result: {result}")
    
    # 5. Verify Agent B received it
    # Since receive_message is async and just logs/stores, we can't easily "return" the value 
    # without inspecting the mock store or monkey-patching.
    # Let's monkey-patch receive_message for verification.
    
    original_receive = agent_b.receive_message
    received_msgs = []
    
    async def intercepted_receive(message):
        received_msgs.append(message)
        await original_receive(message)
        
    agent_b.receive_message = intercepted_receive
    # Re-register because the bus holds the old callback reference
    bus.register_agent("Agent-B", intercepted_receive)
    
    print("\n[Step 2] Sending another message to verify receipt...")
    await comm_tool_a.send_message("Agent-B", "Are you there?")
    
    await asyncio.sleep(0.1) # Yield to allow event loop to process
    
    if len(received_msgs) > 0:
        msg = received_msgs[0]
        print(f"\nSUCCESS: Agent B received message: '{msg.content}' from '{msg.sender}'")
    else:
        print("\nFAILURE: Agent B did not receive the message.")

if __name__ == "__main__":
    asyncio.run(main())
