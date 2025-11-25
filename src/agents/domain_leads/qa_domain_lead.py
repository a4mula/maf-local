"""
QA Domain Lead Agent

Tier 3 agent responsible for breaking down QA and testing tasks into
atomic subtasks for the TesterExecutor.
"""

from src.agents.domain_leads.base_domain_lead import BaseDomainLead
from src.workflows.tlb_workflow import TLBWorkflow
from src.utils import get_logger

logger = get_logger(__name__)

class QADomainLead(BaseDomainLead):
    """
    Tier 3: QA Domain Lead
    
    Responsibilities:
    1. Receive high-level QA tasks from Project Lead
    2. Break down into atomic test creation/execution tasks
    3. Route to TesterExecutor via TLB
    """
    def __init__(self, chat_client, tlb_workflow: TLBWorkflow):
        super().__init__(
            chat_client=chat_client,
            domain="QA",
            tlb_workflow=tlb_workflow,
            instructions="""
            You are the QA Domain Lead.
            
            Your specific focus is SOFTWARE QUALITY ASSURANCE.
            
            When breaking down tasks, prioritize:
            1. Unit tests for individual components
            2. Integration tests for workflows
            3. E2E tests for full user journeys
            4. Regression testing for critical paths
            
            Delegate all test writing and execution to the "tester" executor.
            """
        )
