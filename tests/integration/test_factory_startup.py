import pytest
from src.services.agent_factory import AgentFactory
from src.agents.liaison_agent import LiaisonAgent
from src.agents.project_lead_agent import ProjectLeadAgent

def test_factory_startup():
    """
    Verify that AgentFactory can instantiate the simplified hierarchy.
    """
    hierarchy = AgentFactory.create_hierarchy()
    
    assert "liaison" in hierarchy
    assert "project_lead" in hierarchy
    
    liaison = hierarchy["liaison"]
    project_lead = hierarchy["project_lead"]
    
    assert isinstance(liaison, LiaisonAgent)
    assert isinstance(project_lead, ProjectLeadAgent)
    
    # Check dependency injection
    assert liaison.project_lead == project_lead
    
    print("Factory startup verification passed!")

if __name__ == "__main__":
    test_factory_startup()
