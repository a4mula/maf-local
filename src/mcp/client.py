import asyncio
import json
import sys
from typing import List, Dict, Any, Optional

class MCPClient:
    """
    A lightweight Async Client for the Model Context Protocol (MCP).
    Communicates with an MCP Server via JSON-RPC over Stdio.
    """
    def __init__(self, command: str, args: List[str]):
        self.command = command
        self.args = args
        self.process: Optional[asyncio.subprocess.Process] = None
        self._msg_id = 0

    async def connect(self):
        """Starts the MCP Server subprocess."""
        print(f"[MCP] Connecting to server: {self.command} {' '.join(self.args)}")
        self.process = await asyncio.create_subprocess_exec(
            self.command, *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("[MCP] Connected.")

    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Sends a JSON-RPC request and waits for the response."""
        if not self.process:
            raise RuntimeError("MCP Client not connected.")

        self._msg_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._msg_id,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        # Read response (assuming one line per response for this lightweight impl)
        # In a robust impl, we'd need a proper reader loop handling async notifications
        line = await self.process.stdout.readline()
        if not line:
            raise RuntimeError("Server closed connection.")
            
        response = json.loads(line.decode())
        
        if "error" in response:
            raise RuntimeError(f"MCP Error: {response['error']}")
            
        return response.get("result")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Queries the server for available tools."""
        result = await self._send_request("tools/list")
        return result.get("tools", [])

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Executes a tool on the server."""
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        return result.get("content", [])

    async def close(self):
        """Terminates the server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("[MCP] Disconnected.")
