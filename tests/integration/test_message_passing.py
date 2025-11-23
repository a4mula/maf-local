import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.agents.liaison_agent import LiaisonAgent
from src.agents.project_lead_agent import ProjectLeadAgent

@pytest.mark.asyncio
async def test_liaison_forwards_idea_to_project_lead():
    """
    Verify that LiaisonAgent forwards 'IDEA' intent messages to ProjectLeadAgent.
    """
    # Mock Client
    mock_client = MagicMock()
    
    # Mock Project Lead
    mock_project_lead = MagicMock(spec=ProjectLeadAgent)
    mock_project_lead.receive_idea = AsyncMock(return_value="Idea received and processed.")
    
    # Instantiate Liaison
    liaison = LiaisonAgent(project_lead=mock_project_lead, chat_client=mock_client)
    
    # Mock the SDK agent inside Liaison to return "IDEA" intent
    mock_sdk_agent = AsyncMock()
    mock_sdk_agent.run.return_value = "IDEA"
    liaison.sdk_agent = mock_sdk_agent
    
    # Execute
    user_message = "Let's build a rocket ship."
    response = await liaison.handle_user_message(user_message)
    
    # Verify
    # 1. Check intent classification was called
    mock_sdk_agent.run.assert_called()
    
    # 2. Check Project Lead was called
    mock_project_lead.receive_idea.assert_called_once_with(user_message)
    
    # 3. Check response contains the Project Lead's response
    assert "Idea received and processed" in response
    
    print("Message passing verification passed!")

if __name__ == "__main__":
    # Run the async test
    import asyncio
    asyncio.run(test_liaison_forwards_idea_to_project_lead())
