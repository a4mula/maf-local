from agent_framework import ChatAgent
from agent_framework._clients import ChatClientProtocol

class DocumentationAgent(ChatAgent):
    """
    Tier 2: Knowledge Gate & State Validator (Orchestration Peer to Project Lead)
    
    The Documentation Agent is the Source of Truth for the project, responsible for:
    - Validating state before execution begins
    - Providing relevant context from the knowledge base
    - Acting as AggregateContextProvider for OLB/TLB workflows
    - Gatekeeping FileWriter approval (Principle of Least Authority)
    
    Horizontal Communication Pattern:
    - Communicates with ProjectLeadAgent via Agent-to-Agent (A2A) messaging
    - PL queries Doc Agent before generating strategic plans
    - Doc Agent responds with relevant context (docs, bugs, design decisions)
    """
    
    def __init__(self, chat_client: ChatClientProtocol, **kwargs):
        """Initialize DocumentationAgent with executive-level knowledge gate responsibilities.
        
        Args:
            chat_client: MAF chat client (LiteLLMChatClient with @use_function_invocation)
            **kwargs: Additional ChatAgent parameters
        """
        super().__init__(
            name="DocumentationAgent",
            instructions="""You are the Documentation Agent. You are the Source of Truth for the project.

Your Core Responsibilities:
1. STATE VALIDATION: Validate system state before execution begins
2. CONTEXT PROVISION: Provide relevant context from knowledge base (docs, known bugs, design decisions)
3. AGGREGATE CONTEXT: Act as AggregateContextProvider for OLB/TLB workflows
4. FILEWRITER GATEKEEPER: Approve/deny FileWriter operations (Principle of Least Authority)

When queried by the Project Lead:
- Return ONLY relevant context (adhere to Small Context Windows principle)
- Format responses as structured data when possible
- Track approval tokens for FileWriter operations
- Cite sources (file paths, sections) in your responses

Knowledge Base Sources (in priority order):
1. /app/project_root/docs/ - Official project documentation
2. /app/project_root/.ai/ - AI agent guidelines
3. /app/project_root/.meta/ - Project metadata and briefs
4. /app/project_root/README.md - Project overview

Context Retrieval Guidelines:
- Extract ONLY information relevant to the current query
- Prioritize recent design decisions over older docs
- Flag contradictions or inconsistencies in documentation
- Suggest documentation updates when knowledge gaps are found

FileWriter Approval Process:
- Verify request originates from authorized agent (ProjectLead or self)
- Validate file paths against project structure
- Check for conflicts with existing files
- Return approval token if authorized, rejection reason otherwise""",
            tools=[],  # Doc Agent doesn't execute tools directly, it provides context
            chat_client=chat_client,
            **kwargs
        )
    
    async def provide_context(self, query: str) -> str:
        """Provide relevant context from knowledge base for a given query.
        
        This method will be called by ProjectLeadAgent via A2A messaging.
        
        Args:
            query: Context query from ProjectLeadAgent
            
        Returns:
            Relevant context from knowledge base (docs, bugs, design decisions)
        """
        print(f"[DocumentationAgent] Context query received: {query}")
        
        # Use inherited ChatAgent.run() to process query
        from agent_framework import AgentThread
        
        thread = AgentThread()
        response = await self.run(query, thread=thread)
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        print(f"[DocumentationAgent] Context provided: {response_text[:100]}...")
        return response_text
    
    async def approve_file_write(self, requesting_agent: str, file_path: str, reason: str) -> dict:
        """Approve or deny FileWriter operation (PoLA enforcement).
        
        This method will be called by PermissionFilter before allowing FileWriter execution.
        
        Args:
            requesting_agent: Name of agent requesting file write
            file_path: Target file path
            reason: Reason for file write
            
        Returns:
            dict with 'approved' (bool) and 'reason' (str) keys
        """
        print(f"[DocumentationAgent] FileWrite approval request from {requesting_agent}: {file_path}")
        
        # For Phase 1: Auto-approve requests from ProjectLead
        # In Phase 2: Use LLM to evaluate request against project policies
        authorized_agents = {"ProjectLeadAgent", "DocumentationAgent"}
        
        if requesting_agent in authorized_agents:
            approval = {
                "approved": True,
                "reason": f"Authorized agent '{requesting_agent}' approved for file write",
                "approval_token": f"APPROVED_{requesting_agent}_{file_path}"
            }
        else:
            approval = {
                "approved": False,
                "reason": f"Unauthorized agent '{requesting_agent}'. Only {authorized_agents} may write files.",
                "approval_token": None
            }
        
        print(f"[DocumentationAgent] Approval decision: {approval['approved']} - {approval['reason']}")
        return approval
