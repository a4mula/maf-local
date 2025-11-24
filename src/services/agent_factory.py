from src.agents import (
    LiaisonAgent,
    ProjectLeadAgent
)
from src.agents.documentation_agent import DocumentationAgent

class AgentFactory:
    """
    Factory to instantiate MAF Studio agents.
    
    Phase 1 (Current): Tier 1 + Tier 2 Orchestration
    - Liaison (Tier 1)
    - ProjectLead (Tier 2 Orchestration)
    - DocumentationAgent (Tier 2 Orchestration - peer to PL)
    
    Phase 2 (Future): Add Domain Leads + Executors
    """
    @staticmethod
    def create_hierarchy(message_store=None):
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        # Create shared chat client (MAF-compliant with @use_function_invocation)
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)

        # Tier 2: Orchestration (Peers)
        project_lead = ProjectLeadAgent(chat_client=client)
        documentation_agent = DocumentationAgent(chat_client=client)

        # Tier 1: Interface
        liaison = LiaisonAgent(project_lead=project_lead, chat_client=client)

        return {
            "liaison": liaison,
            "project_lead": project_lead,
            "documentation_agent": documentation_agent,  # NEW in Phase 1
            "domain_leads": {},  # Phase 2
            "executors": {},     # Phase 2
            "dependencies": {}   # Phase 2
        }
