from src.agents import (
    LiaisonAgent,
    ProjectLeadAgent,
    DomainLeadAgent,
    ExecutorAgent,
    GovernanceAgent,
    ContextRetrievalAgent,
    ArtifactManagerAgent
)

class AgentFactory:
    """
    Factory to instantiate the Hierarchical MAF Studio agents.
    """
    @staticmethod
    def create_hierarchy(message_store=None):
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings
        
        # Create shared chat client
        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)

        # 1. Create Dependencies (Phase 2 & 4 skeletons)
        if message_store is None:
            # Fallback or error in real app, but for now we assume it's passed
            pass
        
        # Create MAF SDK-compliant memory provider for Context Retrieval Agent
        from src.persistence.chromadb_context_provider import ChromaDBContextProvider
        
        memory_provider = ChromaDBContextProvider(
            host="localhost",  # NOTE: In Docker, this should be "maf-chroma"
            port=8000,
            collection_name="maf_knowledge"
        )
            
        governance = GovernanceAgent(db_store=message_store, chat_client=client)
        context_agent = ContextRetrievalAgent(
            chat_client=client,
            memory_provider=memory_provider  # Inject provider
        )


        # 2. Create Project Lead (Tier 2)
        project_lead = ProjectLeadAgent(governance_agent=governance, chat_client=client)

        # 3. Create Liaison (Tier 1)
        liaison = LiaisonAgent(project_lead=project_lead, chat_client=client)

        # 4. Create Domain Leads (Tier 3)
        dl_dev = DomainLeadAgent(pillar="Development", context_agent=context_agent, chat_client=client)
        dl_qa = DomainLeadAgent(pillar="QA", context_agent=context_agent, chat_client=client)
        dl_docs = DomainLeadAgent(pillar="Documentation", context_agent=context_agent, chat_client=client)

        # 5. Create Executors (Tier 4)
        exec_coder = ExecutorAgent(role="Coder", chat_client=client)
        exec_tester = ExecutorAgent(role="Tester", chat_client=client)
        exec_writer = ExecutorAgent(role="Writer", chat_client=client)

        # 6. Create Artifact Manager (Tier 5)
        artifact_manager = ArtifactManagerAgent(chat_client=client)

        return {
            "liaison": liaison,
            "project_lead": project_lead,
            "domain_leads": {
                "dev": dl_dev,
                "qa": dl_qa,
                "docs": dl_docs
            },
            "executors": {
                "coder": exec_coder,
                "tester": exec_tester,
                "writer": exec_writer
            },
            "dependencies": {
                "governance": governance,
                "context": context_agent,
                "artifact_manager": artifact_manager
            }
        }
