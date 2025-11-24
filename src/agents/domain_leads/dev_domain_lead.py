"""
Dev Domain Lead Agent

Specialized Domain Lead for software development tasks.
Focuses on code architecture, implementation, and testing.
"""

from src.agents.domain_leads.base_domain_lead import BaseDomainLead
from src.workflows.tlb_workflow import TLBWorkflow


class DevDomainLead(BaseDomainLead):
    """Development Domain Lead (Tier 3).
    
    Specializes in:
    - Feature implementation
    - Bug fixes
    - Refactoring
    - Technical architecture
    """
    
    def __init__(self, chat_client, tlb_workflow: TLBWorkflow):
        """Initialize Dev Domain Lead."""
        super().__init__(
            chat_client=chat_client,
            domain="Development",
            tlb_workflow=tlb_workflow,
            instructions="""
            You are the Lead Developer.
            
            Focus on:
            - Clean, maintainable code
            - Test-Driven Development (TDD)
            - Solid architectural patterns
            
            When breaking down tasks:
            1. Always include a TEST task (TesterExecutor)
            2. Always include an IMPLEMENTATION task (CoderExecutor)
            3. Ensure tests cover the implementation
            """
        )
