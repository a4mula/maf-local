"""
Docs Domain Lead Agent

Specialized Domain Lead for documentation tasks.
Focuses on documentation architecture, updates, and maintenance.
"""

from src.agents.domain_leads.base_domain_lead import BaseDomainLead
from src.workflows.tlb_workflow import TLBWorkflow


class DocsDomainLead(BaseDomainLead):
    """Documentation Domain Lead (Tier 3).
    
    Specializes in:
    - Documentation updates (README, guides, API docs)
    - Architectural diagrams
    - Knowledge base maintenance
    - Content consistency
    """
    
    def __init__(self, chat_client, tlb_workflow: TLBWorkflow):
        """Initialize Docs Domain Lead."""
        super().__init__(
            chat_client=chat_client,
            domain="Documentation",
            tlb_workflow=tlb_workflow,
            instructions="""
            You are the Lead Technical Writer and Documentation Manager.
            
            Focus on:
            - Clear, concise, and accurate documentation
            - Keeping documentation in sync with code
            - Maintaining architectural diagrams and decision records (ADRs)
            - Ensuring proper formatting and structure
            
            When breaking down tasks:
            1. Always include a WRITING task (WriterExecutor)
            2. If code analysis is needed, include a small implementation task or ask for context
            3. Ensure validation of links and formatting
            """
        )
