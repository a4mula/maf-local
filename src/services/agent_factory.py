from src.agents import (
    LiaisonAgent,
    ProjectLeadAgent
)
from src.agents.documentation_agent import DocumentationAgent
from src.agents.domain_leads import DevDomainLead
from src.agents.executors import CoderExecutor, TesterExecutor, WriterExecutor
from src.workflows.tlb_workflow import TLBWorkflow
from src.workflows.olb_workflow import OLBWorkflow

class AgentFactory:
    """
    Factory to instantiate MAF Studio agents.
    
    Phase 2 (Current): Full 4-Tier Hierarchy
    - Tier 1: Liaison
    - Tier 2: ProjectLead + DocumentationAgent
    - Tier 3: Domain Leads (Dev)
    - Tier 4: Executors (Coder, Tester, Writer)
    - Workflows: OLB (Strategy->Tactics), TLB (Tactics->Execution)
    """
    @staticmethod
    def create_hierarchy(message_store=None):
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        # Create shared chat client
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)

        # --- Tier 4: Executors ---
        executors = {
            "coder": CoderExecutor(chat_client=client),
            "tester": TesterExecutor(chat_client=client),
            "writer": WriterExecutor(chat_client=client)
        }

        # --- Workflows: TLB ---
        tlb_workflow = TLBWorkflow(executors=executors)

        # --- Tier 3: Domain Leads ---
        dev_dl = DevDomainLead(chat_client=client, tlb_workflow=tlb_workflow)
        # Future: qa_dl, docs_dl

        domain_leads = {
            "Development": dev_dl
        }

        # --- Workflows: OLB ---
        olb_workflow = OLBWorkflow(domain_leads=domain_leads)

        # --- Tier 2: Orchestration ---
        project_lead = ProjectLeadAgent(chat_client=client, olb_workflow=olb_workflow)
        documentation_agent = DocumentationAgent(chat_client=client)

        # --- Tier 1: Interface ---
        liaison = LiaisonAgent(project_lead=project_lead, chat_client=client)

        return {
            "liaison": liaison,
            "project_lead": project_lead,
            "documentation_agent": documentation_agent,
            "domain_leads": domain_leads,
            "executors": executors,
            "workflows": {
                "tlb": tlb_workflow,
                "olb": olb_workflow
            }
        }
