import inspect
import json
import importlib
from typing import List, Dict, Any, Optional, Callable

from src.clients.base import IChatClient
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.settings import settings
from src.config.tool_registry import TOOL_REGISTRY

from src.middleware.message_bus import MessageBus, Message

class CoreAgent:
    """
    The central intelligence layer for the Microsoft Agent Framework (MAF).
    Adheres to the MAF Simple Agent Pattern: Orchestrates tool execution via the Agent Loop.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        client: IChatClient,
        audit_log: AuditLogProvider,
        message_store: MessageStoreProvider,
        registered_tools: List[Dict[str, Any]],
        max_tool_call_depth: int = 5,
        on_step: Optional[Callable[[str, str], Any]] = None # Callback for UI steps (name, type)
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.client = client
        self.audit_log = audit_log
        self.message_store = message_store
        self.registered_tools = registered_tools
        self.max_tool_call_depth = max_tool_call_depth
        self.on_step = on_step
        
        self.bus: Optional[MessageBus] = None # Connection to the Message Bus
        self.tool_instances = {} # Store instances of stateful tools
        self.tool_functions = self._load_tool_functions(registered_tools)

    def _load_tool_functions(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dynamically loads executable functions from tool schemas."""
        tool_functions = {}
        for schema in schemas:
            func_name = schema.get("function_name")
            module_path = schema.get("module_path")
            
            if func_name and module_path:
                try:
                    module = importlib.import_module(module_path)
                    
                    # 1. Try loading as a standalone function (Stateless)
                    if hasattr(module, func_name):
                        candidate = getattr(module, func_name)
                        if callable(candidate):
                            tool_functions[func_name] = candidate
                            continue

                    # 2. Try loading as a method of a class (Stateful)
                    # We scan the module for classes that implement this method
                    found_method = False
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Ensure the class is defined in this module (optional, but safer)
                        if obj.__module__ == module.__name__: 
                            if hasattr(obj, func_name) and callable(getattr(obj, func_name)):
                                # Check if we already have an instance of this class
                                if name not in self.tool_instances:
                                    print(f"[Tooling] Instantiating stateful tool class: {name}")
                                    
                                    # Check if the constructor accepts 'agent' for dependency injection
                                    sig = inspect.signature(obj.__init__)
                                    if 'agent' in sig.parameters:
                                        self.tool_instances[name] = obj(agent=self)
                                    else:
                                        self.tool_instances[name] = obj()
                                
                                instance = self.tool_instances[name]
                                tool_functions[func_name] = getattr(instance, func_name)
                                found_method = True
                                break
                    
                    if not found_method:
                        print(f"[Tooling] WARNING: Could not find function or class method '{func_name}' in {module_path}")

                except Exception as e:
                    print(f"[Tooling] WARNING: Failed to load tool {func_name} from {module_path}. Error: {e}")
        return tool_functions
        return tool_functions

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        """
        Dynamically registers a new tool (e.g., from an MCP server).
        """
        print(f"[CoreAgent] Dynamically registering tool: {name}")
        
        # 1. Add to registered_tools list (for LLM)
        schema = {
            "function_name": name,
            "description": description,
            "parameters": parameters
        }
        self.registered_tools.append(schema)
        
        # 2. Add to executable functions
        self.tool_functions[name] = func

    def connect_bus(self, bus: MessageBus):
        """Connects the agent to the Message Bus."""
        self.bus = bus
        self.bus.register_agent(self.name, self.receive_message)
        print(f"[CoreAgent] {self.name} connected to Message Bus.")

    async def receive_message(self, message: Message):
        """
        Callback for handling incoming messages from the bus.
        Stores the message in the history so the agent sees it in the next turn.
        """
        print(f"[CoreAgent] {self.name} received message from {message.sender}: {message.content}")
        
        # Log to audit log
        await self.audit_log.log(self.name, "MESSAGE_RECEIVED", f"From {message.sender}: {message.content}", self.message_store.session_id)
        
        # Store in message store as a 'user' message (or system, but user makes it actionable)
        # We prefix it to indicate it's an inter-agent message
        formatted_content = f"[Incoming Message from Agent '{message.sender}']: {message.content}"
        await self.message_store.store_message("user", formatted_content)
    def _is_conversational_prompt(self, text: str) -> bool:
        """Heuristic to detect simple greetings and prevent tool exposure."""
        t = text.strip().lower()
        greetings = {'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon'}
        # If input is short (< 5 words) and contains a greeting
        return len(t.split()) < 5 and any(g in t for g in greetings)

    async def process(self, prompt: str) -> str:
        """
        Handles the user prompt, manages conversation history, and orchestrates 
        tool calling (MAF Simple Agent Pattern).
        """
        # 1. Retrieve Current History
        history = await self.message_store.get_history(limit=50)
        history.append({"role": "user", "content": prompt})
        await self.message_store.store_message("user", prompt)

        # 2. Determine Tool Strategy
        # STRATEGY A: Safety - Hide tools for greetings
        if self._is_conversational_prompt(prompt):
            active_tools = None
            tool_choice = None
            print(f"[CoreAgent] Conversational intent detected. Hiding tools.")
        else:
            # STRATEGY B: Compliance - Expose tools and FORCE specific ones if detected
            active_tools = self.registered_tools
            tool_choice = "auto" # Default
            
            # Check for explicit tool requests in the prompt
            for tool_schema in self.registered_tools:
                if tool_schema['function_name'] in prompt:
                    print(f"[CoreAgent] Detected specific tool request: {tool_schema['function_name']}. Forcing tool_choice.")
                    # LiteLLM/OpenAI format for forcing a specific tool
                    tool_choice = {"type": "function", "function": {"name": tool_schema['function_name']}}
                    break

        # Start the conversation loop
        for _ in range(self.max_tool_call_depth):
            
            llm_output = await self.client.chat(
                history=history,
                tools=active_tools, 
                tool_choice=tool_choice
            )

            # 3. Check for MAF Tool Call String (CRITICAL FIX: check for closing >)
            if llm_output.startswith("<call:") and llm_output.endswith(">"):
                try:
                    # Parse: <call:tool_call_id|name:{"arg": "val"}>
                    # Strip <call: from start and > from end
                    content = llm_output[6:-1]
                    
                    # Split on the first colon to separate id|name from JSON args
                    id_and_name, tool_args_json = content.split(':', 1)
                    
                    # CRITICAL FIX: Split the ID from the Name
                    tool_call_id, tool_name = id_and_name.split('|', 1) 
                    
                    # Ensure arguments are parsed as JSON object
                    tool_args = json.loads(tool_args_json)

                    # --- CRITICAL FIX START: Store the LLM's Tool Call Turn ---
                    # The LLM's response was a tool call. We must append this response to history
                    # *before* the tool result, so LiteLLM can correctly link the response.
                    assistant_tool_call_message = {
                        "role": "assistant",
                        "content": None, # Content is None for tool-call only responses
                        "tool_calls": [
                            {
                                "id": tool_call_id,
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_args_json
                                },
                                "type": "function"
                            }
                        ]
                    }
                    history.append(assistant_tool_call_message)
                    # --- CRITICAL FIX END ---

                    # --- CRITICAL FIX END ---

                    print(f"[Tool Execution] Executing {tool_name} with {tool_args}")
                    await self.audit_log.log(self.name, "TOOL_CALL_REQUEST", f"{tool_name}: {tool_args_json}", self.message_store.session_id)
                    
                    # Notify UI
                    if self.on_step:
                        await self.on_step(tool_name, "tool_call", tool_args)

                    if tool_name in self.tool_functions:
                        func = self.tool_functions[tool_name]
                        # Handle both async and sync functions
                        if inspect.iscoroutinefunction(func):
                            tool_result = await func(**tool_args)
                        else:
                            tool_result = func(**tool_args)
                    else:
                        tool_result = f"Error: Tool '{tool_name}' not found."

                    tool_result_str = str(tool_result)

                    # Update History with Tool Result
                    # This must immediately follow the assistant's tool call message
                    history.append({
                        "role": "tool", 
                        "content": tool_result_str, 
                        "tool_call_id": tool_call_id
                    })
                    
                    await self.audit_log.log(self.name, "TOOL_CALL_RESULT", f"Result: {tool_result_str[:100]}...", self.message_store.session_id)
                    
                    # Reset tool_choice to auto for the follow-up turn so it can chat about the result
                    tool_choice = "auto" 
                    
                    # Continue the loop to send the result back to the LLM for final answer
                    continue
                    
                except Exception as e:
                    error_msg = f"Tool execution failed: {e}"
                    print(f"[CoreAgent Error] {error_msg}")
                    return error_msg

            # 4. Final Text Response
            # If the output wasn't a tool call, it's the final answer.
            await self.message_store.store_message("assistant", llm_output)
            await self.audit_log.log(self.name, "FINAL_RESPONSE", llm_output, self.message_store.session_id)
            return llm_output

        return "Max tool call depth reached."
