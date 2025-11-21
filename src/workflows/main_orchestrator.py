import asyncio
from typing import Dict, Any, Callable, List, Optional, Union
import uuid

# Type alias for the context
WorkflowContext = Dict[str, Any]

class WorkflowNode:
    """
    Represents a node in the workflow graph.
    A node wraps a callable (function or agent) that performs a task.
    """
    def __init__(self, name: str, handler: Callable[[WorkflowContext], Any]):
        self.name = name
        self.handler = handler

    async def execute(self, context: WorkflowContext) -> Any:
        """Executes the node's handler with the given context."""
        if asyncio.iscoroutinefunction(self.handler):
            return await self.handler(context)
        else:
            return self.handler(context)

class WorkflowGraph:
    """
    A directed graph that orchestrates the execution of nodes based on conditions.
    """
    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {} # node_name -> list of {target, condition}
        self.start_node: Optional[str] = None

    def add_node(self, name: str, handler: Callable[[WorkflowContext], Any]):
        """Adds a node to the graph."""
        node = WorkflowNode(name, handler)
        self.nodes[name] = node
        if self.start_node is None:
            self.start_node = name # First node added is default start
        return self

    def add_edge(self, from_node: str, to_node: str, condition: Optional[Callable[[WorkflowContext], bool]] = None):
        """
        Adds a directed edge between two nodes.
        If a condition is provided, the edge is only followed if the condition returns True.
        """
        if from_node not in self.nodes:
            raise ValueError(f"Source node '{from_node}' not found.")
        if to_node not in self.nodes:
            raise ValueError(f"Target node '{to_node}' not found.")

        if from_node not in self.edges:
            self.edges[from_node] = []
        
        self.edges[from_node].append({
            "target": to_node,
            "condition": condition
        })
        return self

    def set_start_node(self, name: str):
        """Explicitly sets the starting node."""
        if name not in self.nodes:
            raise ValueError(f"Node '{name}' not found.")
        self.start_node = name
        return self

    async def run(self, initial_context: Optional[WorkflowContext] = None) -> WorkflowContext:
        """
        Executes the workflow starting from the start_node.
        Returns the final context.
        """
        context = initial_context or {}
        current_node_name = self.start_node
        
        if not current_node_name:
            raise ValueError("Workflow has no start node.")

        print(f"[Workflow] Starting execution at '{current_node_name}'")

        while current_node_name:
            current_node = self.nodes[current_node_name]
            
            # Execute the node
            try:
                print(f"[Workflow] Executing Node: {current_node_name}")
                result = await current_node.execute(context)
                
                # Store result in context (convention: result is stored under 'last_result' or specific key)
                # For simplicity, we assume the handler updates the context in place or returns a dict to merge
                if isinstance(result, dict):
                    context.update(result)
                context["_last_node"] = current_node_name
                context["_last_result"] = result
                
            except Exception as e:
                print(f"[Workflow] Error in node '{current_node_name}': {e}")
                raise e

            # Determine next node
            next_node_name = None
            edges = self.edges.get(current_node_name, [])
            
            for edge in edges:
                condition = edge["condition"]
                target = edge["target"]
                
                if condition is None:
                    # Unconditional edge - take it
                    next_node_name = target
                    break
                elif condition(context):
                    # Conditional edge met - take it
                    next_node_name = target
                    break
            
            if next_node_name:
                print(f"[Workflow] Transitioning: {current_node_name} -> {next_node_name}")
            else:
                print(f"[Workflow] End of path reached at '{current_node_name}'")
            
            current_node_name = next_node_name

        return context
