"""
Universal Tool System - Framework-Agnostic Tool Definitions

This module provides a central tool registry that can export tools in different formats:
- MAF SDK format (Python callables with type annotations)
- LiteLLM/OpenAI format (JSON schemas)
- Ollama format (function definitions)

Tools are defined once and adapted to each framework's requirements.
"""

from typing import Callable, Any, Dict, List, get_type_hints, Annotated
from pydantic import Field
from inspect import signature, Parameter
import json


class UniversalTool:
    """
    Framework-agnostic tool definition.
    
    Stores a tool's function, metadata, and can export to different formats.
    """
    
    def __init__(
        self,
        func: Callable,
        name: str = None,
        description: str = None,
        roles: List[str] = None
    ):
        """
        Initialize a universal tool.
        
        Args:
            func: The actual Python function to execute
            name: Optional override for function name
            description: Optional override for function description
            roles: Optional list of allowed roles (if None, allowed for all)
        """
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip()
        self.roles = roles or []
        
        # Extract parameter information from type hints
        self.parameters = self._extract_parameters()
    
    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract parameter schema from function signature and type hints."""
        sig = signature(self.func)
        hints = get_type_hints(self.func, include_extras=True)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Skip 'caller_role' if it's injected by the framework
            if param_name == 'caller_role':
                continue
                
            param_type = hints.get(param_name, Any)
            
            # Handle Annotated types with Field descriptions
            if hasattr(param_type, '__metadata__'):
                # This is an Annotated type
                base_type = param_type.__origin__
                metadata = param_type.__metadata__
                
                # Extract Field description
                description = ""
                for meta in metadata:
                    if isinstance(meta, type(Field())):
                        description = meta.description or ""
                        break
                
                properties[param_name] = {
                    "type": self._python_type_to_json_type(base_type),
                    "description": description
                }
            else:
                properties[param_name] = {
                    "type": self._python_type_to_json_type(param_type),
                    "description": ""
                }
            
            # Check if required (no default value)
            if param.default == Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def _python_type_to_json_type(self, python_type) -> str:
        """Convert Python type to JSON Schema type."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return type_map.get(python_type, "string")
    
    def to_maf_format(self) -> Callable:
        """Export as MAF SDK format (the actual Python function)."""
        return self.func
    
    def to_litellm_format(self) -> Dict[str, Any]:
        """Export as LiteLLM/OpenAI tool format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def to_ollama_format(self) -> Dict[str, Any]:
        """Export as Ollama function format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    async def execute(self, caller_role: str = None, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        import asyncio
        import inspect
        
        # Check role access
        if self.roles and caller_role not in self.roles:
            raise PermissionError(f"Access denied: Role '{caller_role}' is not authorized to use tool '{self.name}'. Required roles: {self.roles}")
        
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        else:
            return self.func(**kwargs)


class ToolRegistry:
    """
    Central registry for all tools.
    
    Provides framework-specific exports.
    """
    
    def __init__(self):
        self.tools: Dict[str, UniversalTool] = {}
    
    def register(self, func: Callable = None, *, name: str = None, description: str = None, roles: List[str] = None):
        """Register a tool function."""
        def decorator(f):
            tool = UniversalTool(f, name, description, roles)
            self.tools[tool.name] = tool
            return f
            
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def get_maf_tools(self) -> List[Callable]:
        """Get tools in MAF SDK format (Python callables)."""
        return [tool.to_maf_format() for tool in self.tools.values()]
    
    def get_litellm_tools(self) -> List[Dict[str, Any]]:
        """Get tools in LiteLLM/OpenAI format."""
        return [tool.to_litellm_format() for tool in self.tools.values()]
    
    def get_ollama_tools(self) -> List[Dict[str, Any]]:
        """Get tools in Ollama format."""
        return [tool.to_ollama_format() for tool in self.tools.values()]
    
    def get_ai_functions(self) -> List[Any]:
        """Get tools as MAF AIFunction objects."""
        from agent_framework import ai_function
        return [ai_function(tool.func) for tool in self.tools.values()]
    
    def get_tool(self, name: str) -> UniversalTool:
        """Get a specific tool by name."""
        return self.tools.get(name)
    
    async def execute_tool(self, name: str, caller_role: str = None, **kwargs) -> Any:
        """Execute a tool by name with given arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return await tool.execute(caller_role=caller_role, **kwargs)


# Global registry instance
registry = ToolRegistry()
