from agent_framework import Workflow, WorkflowBuilder
from src.persistence.checkpoint_storage import PostgreSQLCheckpointStorage
from src.agents.project_lead_agent import ProjectLeadAgent
from src.agents.domain_lead_agent import DomainLeadAgent

def create_development_workflow(
    project_lead: ProjectLeadAgent,
    domain_lead: DomainLeadAgent,
    checkpoint_storage: PostgreSQLCheckpointStorage
) -> Workflow:
    """
    Creates a MAF-native workflow for development tasks using WorkflowBuilder.
    """
    builder = WorkflowBuilder(name="DevelopmentWorkflow")
    
    # Add agents (wrapped automatically by builder)
    # We use the underlying sdk_agent from our wrapper classes
    builder.add_agent(project_lead.sdk_agent, id="project_lead")
    builder.add_agent(domain_lead.sdk_agent, id="domain_lead")
    
    # Define flow: Project Lead -> Domain Lead
    # This means PL's output is sent to DL
    builder.set_start_executor(project_lead.sdk_agent)
    builder.add_edge(project_lead.sdk_agent, domain_lead.sdk_agent)
    
    # Enable checkpointing
    builder.with_checkpointing(checkpoint_storage)
    
    return builder.build()
