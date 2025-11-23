from src.agents import (
    LiaisonAgent,
    ProjectLeadAgent
)

class AgentFactory:
    """
    Factory to instantiate the Simplified MAF Studio agents.
    Retains only Liaison and Project Lead for MVP.
    """
    @staticmethod
    def create_hierarchy(message_store=None):
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        # Create shared chat client (now MAF-compliant with @use_function_invocation)
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)

        # 1. Create Project Lead (Tier 2)
        # Now uses standard ChatAgent internally
        project_lead = ProjectLeadAgent(chat_client=client)

        # 2. Create Liaison (Tier 1)
        liaison = LiaisonAgent(project_lead=project_lead, chat_client=client)

        return {
            "liaison": liaison,
            "project_lead": project_lead,
            "domain_leads": {}, # Empty for now
            "executors": {},    # Empty for now
            "dependencies": {}  # Empty for now
        }
