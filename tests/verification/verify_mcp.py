import asyncio
import sys
from src.mcp.client import MCPClient
from src.agents.core_agent import CoreAgent

# Mock dependencies
class MockAuditLog:
    async def log(self, *args): pass

class MockMessageStore:
    def __init__(self): self.session_id = "test-mcp"
    async def store_message(self, *args): pass
    async def get_history(self, *args, **kwargs): return []

class MockClient:
    async def chat(self, history, tools, tool_choice):
        # Simulate LLM calling the tool
        last_msg = history[-1]
        if last_msg["role"] == "user" and "add" in last_msg["content"]:
            return '<call:call_1|add_numbers:{"a": 10, "b": 20}>'
        return "The result is 30."

async def main():
    print("--- Verifying MCP Integration ---")
    
    # 1. Start MCP Client
    # We run the mock server using python
    cmd = sys.executable
    args = ["mock_mcp_server.py"]
    
    client = MCPClient(cmd, args)
    await client.connect()
    
    try:
        # 2. List Tools
        print("\n[Step 1] Listing tools from MCP Server...")
        tools = await client.list_tools()
        print(f"Tools found: {[t['name'] for t in tools]}")
        
        if not tools or tools[0]['name'] != 'add_numbers':
            print("FAILURE: Could not list tools.")
            return

        # 3. Register with CoreAgent
        agent = CoreAgent("MCP-Agent", "", MockClient(), MockAuditLog(), MockMessageStore(), [])
        
        print("\n[Step 2] Registering 'add_numbers' with CoreAgent...")
        
        # Create a wrapper function for the tool
        async def add_numbers_wrapper(a, b):
            print(f"[MCP Wrapper] Calling tool 'add_numbers' with a={a}, b={b}")
            result = await client.call_tool("add_numbers", {"a": a, "b": b})
            # Extract text content
            text = result[0]['text']
            return text

        # Register it
        tool_info = tools[0]
        agent.register_tool(
            name=tool_info['name'],
            description=tool_info['description'],
            parameters=tool_info['inputSchema'],
            func=add_numbers_wrapper
        )
        
        # 4. Simulate Agent Loop
        print("\n[Step 3] Simulating Agent Loop...")
        response = await agent.process("Please add 10 and 20.")
        print(f"Agent Response: {response}")
        
        if "30" in response or "The result is 30" in response:
            print("\nSUCCESS: Agent successfully called MCP tool.")
        else:
            print("\nFAILURE: Agent did not produce expected result.")
            
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
