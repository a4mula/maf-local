"""
Full Hierarchy Integration Test (Step 10)

Tests the complete UBE flow from Project Lead down to Executors and back.
Uses AgentFactory to create the real production hierarchy.

Flow:
1. Project Lead receives user request
2. PL creates StrategicPlan via OLB
3. OLB routes to DevDomainLead
4. DevDL breaks down task via TLB
5. Executors (Coder/Tester) execute tasks
6. Results bubble up to PL
"""

import pytest
from agent_framework import AgentThread
from src.services.agent_factory import AgentFactory
from src.models.data_contracts import StrategicPlan

class TestFullHierarchy:
    """End-to-end integration tests for the UBE architecture."""
    
    @pytest.fixture
    def hierarchy(self):
        """Create full agent hierarchy using factory."""
        return AgentFactory.create_hierarchy()
        
    @pytest.mark.asyncio
    async def test_e2e_feature_creation(self, hierarchy):
        """
        Scenario: User asks to create a simple 'add' function.
        Expectation: 
        - PL creates plan
        - DevDL executes plan
        - Coder writes code
        - Tester writes test
        - PL reports success
        """
        project_lead = hierarchy["project_lead"]
        
        # Verify hierarchy is wired correctly
        assert project_lead.olb_workflow is not None
        assert "Development" in hierarchy["domain_leads"]
        dev_dl = hierarchy["domain_leads"]["Development"]
        assert dev_dl.tlb_workflow is not None
        
        # Simulate user request
        user_request = "Create a Python function 'add(a, b)' that returns the sum. Include a test."
        
        print(f"\n[E2E] Sending request to Project Lead: {user_request}")
        
        # We need to mock the LLM response for the Project Lead to ensure it calls the tool
        # correctly without relying on a real LLM call which might be flaky or slow.
        # However, for a true integration test, we want to exercise the tool calling mechanics.
        # Since we can't easily mock the internal LLM of the agent in this setup without
        # patching the client, we will call the *tool* directly on the PL to simulate
        # the PL's decision to execute.
        
        # 1. Simulate PL decision to use the tool
        print("[E2E] Simulating PL tool usage...")
        result = await project_lead.submit_strategic_plan_tool(
            target_domains=["Development"],
            tasks=[
                {
                    "description": "Implement 'add(a, b)' function in Python", 
                    "domain": "Development",
                    "task_id": "task_add_func"
                },
                {
                    "description": "Create unit test for 'add(a, b)'", 
                    "domain": "Development",
                    "task_id": "task_add_test"
                }
            ],
            plan_context=user_request
        )
        
        print(f"[E2E] Execution Result:\n{result}")
        
        # Verify success
        assert "Plan Execution Result: Completed" in result
        assert "task_add_func" in result
        assert "task_add_test" in result
        
        # Verify artifacts exist in the result summary
        # (The result string contains the stringified dictionary)
        assert "Completed" in result
        assert "Failed" not in result.split("Summary:")[0] # Check status line
