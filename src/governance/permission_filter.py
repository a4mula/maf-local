"""
Governance module for MAF-Local.

Implements security and compliance policies following MAF SDK standards:
- PermissionFilter: Enforces Principle of Least Authority (PoLA) over tool execution
- GovernanceException: Raised when governance policies are violated
"""

from agent_framework import FunctionMiddleware, FunctionInvocationContext
from src.utils import get_logger

logger = get_logger(__name__)


class GovernanceException(Exception):
    """Raised when governance policies are violated."""
    pass


class PermissionFilter(FunctionMiddleware):
    """Enforces Principle of Least Authority (PoLA) over function/tool execution.
    
    This middleware intercepts AIFunction invocations and enforces authorization
    rules. Currently enforces:
    - FileWriter can ONLY be called by DocumentationAgent or ProjectLeadAgent
    
    Future enhancements:
    - Rate limiting per agent
    - Resource quota enforcement
    - Audit trail for sensitive operations
    
    This is a MAF-compliant FunctionMiddleware that processes FunctionInvocationContext.
    
    Examples:
        .. code-block:: python
        
            from agent_framework import ChatAgent
            from src.governance.permission_filter import PermissionFilter
            
            # Use with an agent
            agent = ChatAgent(chat_client=client, name="ProjectLead", middleware=PermissionFilter())
    """
    
    AUTHORIZED_FILE_WRITERS = {"DocumentationAgent", "ProjectLeadAgent"}
    
    async def process(
        self,
        context: FunctionInvocationContext,
        next
    ) -> None:
        """Process a function invocation and enforce permission checks.
        
        Args:
            context: Function invocation context from MAF containing function, arguments, and metadata.
            next: Function to call the next middleware or final function execution.
            
        Raises:
            GovernanceException: If permission check fails (unauthorized agent attempting file write).
        
        Note:
            Middleware should not return anything. All data manipulation happens
            within the context object. We can set context.result to override execution,
            or observe context.result after calling next() for actual results.
        """
        
        # Check if this is a FileWriter function call
        function_name = context.function.name if hasattr(context.function, 'name') else None
        
        if function_name == "FileWriter" or function_name == "write_file":
            # Extract calling agent name from metadata (injected by agent runtime)
            agent_name = context.metadata.get('agent_name', context.kwargs.get('agent_name', 'Unknown'))
            
            # Enforce authorization
            if agent_name not in self.AUTHORIZED_FILE_WRITERS:
                raise GovernanceException(
                    f"Unauthorized disk access. Agent '{agent_name}' is not authorized to call FileWriter. "
                    f"Authorized agents: {self.AUTHORIZED_FILE_WRITERS}"
                )
            
            # Log approved access (audit trail)
            logger.info(f"[PermissionFilter] ✓ Approved FileWriter call from '{agent_name}'")
        
        # Proceed to next middleware or function execution
        await next(context)

