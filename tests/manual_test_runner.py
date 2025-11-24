#!/usr/bin/env python3
"""
Manual test runner for Phase 1 U.B.E. implementation.

This script validates Phase 1 components without requiring pytest:
- ProjectLeadAgent MAF compliance
- DocumentationAgent creation
- PermissionFilter enforcement
- AFBaseSettings data contracts
- Agent factory integration

Run with: python3 manual_test_runner.py
"""

import sys
import traceback
from typing import List, Tuple

# Test results tracking
test_results: List[Tuple[str, bool, str]] = []


def test_result(name: str, passed: bool, message: str = ""):
    """Record a test result."""
    test_results.append((name, passed, message))
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message and not passed:
        print(f"  Error: {message}")


def run_test_suite():
    """Run all Phase 1 validation tests."""
    print("=" * 80)
    print("Phase 1 U.B.E. Manual Test Runner")
    print("=" * 80)
    print()

    # Test 1: Import core modules
    print("### Test Group: Core Imports ###")
    try:
        from src.agents.project_lead_agent import ProjectLeadAgent
        test_result("Import ProjectLeadAgent", True)
    except Exception as e:
        test_result("Import ProjectLeadAgent", False, str(e))
        return

    try:
        from src.agents.documentation_agent import DocumentationAgent
        test_result("Import DocumentationAgent", True)
    except Exception as e:
        test_result("Import DocumentationAgent", False, str(e))
        return

    try:
        from src.governance.permission_filter import PermissionFilter, GovernanceException
        test_result("Import PermissionFilter", True)
    except Exception as e:
        test_result("Import PermissionFilter", False, str(e))
        return

    try:
        from src.models.data_contracts import TaskDefinition, StrategicPlan, ExecutorReport
        test_result("Import data contracts", True)
    except Exception as e:
        test_result("Import data contracts", False, str(e))
        return

    try:
        from src.services.agent_factory import AgentFactory
        test_result("Import AgentFactory", True)
    except Exception as e:
        test_result("Import AgentFactory", False, str(e))
        return

    print()

    # Test 2: MAF Compliance
    print("### Test Group: MAF Compliance ###")
    try:
        from agent_framework import ChatAgent
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings

        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        pl_agent = ProjectLeadAgent(chat_client=client)

        # CRITICAL: ProjectLeadAgent must inherit from ChatAgent
        if isinstance(pl_agent, ChatAgent):
            test_result("ProjectLeadAgent inherits from ChatAgent (CRITICAL)", True)
        else:
            test_result("ProjectLeadAgent inherits from ChatAgent (CRITICAL)", False,
                       f"Expected ChatAgent, got {type(pl_agent)}")

        # Check for inherited methods
        if hasattr(pl_agent, 'run') and callable(pl_agent.run):
            test_result("ProjectLeadAgent has run() method", True)
        else:
            test_result("ProjectLeadAgent has run() method", False)

    except Exception as e:
        test_result("ProjectLeadAgent MAF compliance check", False, str(e))
        traceback.print_exc()

    print()

    # Test 3: DocumentationAgent
    print("### Test Group: DocumentationAgent ###")
    try:
        from agent_framework import ChatAgent
        from src.clients.litellm_client import LiteLLMChatClient
        from src.config.settings import settings

        client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
        doc_agent = DocumentationAgent(chat_client=client)

        # Check inheritance
        if isinstance(doc_agent, ChatAgent):
            test_result("DocumentationAgent inherits from ChatAgent", True)
        else:
            test_result("DocumentationAgent inherits from ChatAgent", False,
                       f"Expected ChatAgent, got {type(doc_agent)}")

        # Check methods
        if hasattr(doc_agent, 'provide_context') and callable(doc_agent.provide_context):
            test_result("DocumentationAgent has provide_context() method", True)
        else:
            test_result("DocumentationAgent has provide_context() method", False)

        if hasattr(doc_agent, 'approve_file_write') and callable(doc_agent.approve_file_write):
            test_result("DocumentationAgent has approve_file_write() method", True)
        else:
            test_result("DocumentationAgent has approve_file_write() method", False)

    except Exception as e:
        test_result("DocumentationAgent validation", False, str(e))
        traceback.print_exc()

    print()

    # Test 4: Data Contracts
    print("### Test Group: Data Contracts ###")
    try:
        from src.models.data_contracts import TaskDefinition, StrategicPlan, ExecutorReport

        # Test TaskDefinition
        task = TaskDefinition(
            task_id="test_001",
            domain="Frontend",
            description="Test task"
        )
        if task.task_id == "test_001":
            test_result("TaskDefinition creation and validation", True)
        else:
            test_result("TaskDefinition creation and validation", False)

        # Test StrategicPlan
        plan = StrategicPlan(
            plan_id="plan_001",
            target_domains=["Frontend"],
            tasks=[task]
        )
        if len(plan.tasks) == 1:
            test_result("StrategicPlan creation and validation", True)
        else:
            test_result("StrategicPlan creation and validation", False)

        # Test ExecutorReport
        report = ExecutorReport(
            executor_task_id="test_001",
            executor_name="TestExecutor",
            status="Completed"
        )
        if report.status == "Completed":
            test_result("ExecutorReport creation and validation", True)
        else:
            test_result("ExecutorReport creation and validation", False)

    except Exception as e:
        test_result("Data contracts validation", False, str(e))
        traceback.print_exc()

    print()

    # Test 5: Agent Factory
    print("### Test Group: Agent Factory ###")
    try:
        from src.services.agent_factory import AgentFactory

        hierarchy = AgentFactory.create_hierarchy()

        # Check for all Phase 1 agents
        if "liaison" in hierarchy:
            test_result("Factory creates Liaison", True)
        else:
            test_result("Factory creates Liaison", False)

        if "project_lead" in hierarchy:
            test_result("Factory creates ProjectLead", True)
        else:
            test_result("Factory creates ProjectLead", False)

        if "documentation_agent" in hierarchy:
            test_result("Factory creates DocumentationAgent", True)
        else:
            test_result("Factory creates DocumentationAgent", False, "Missing from hierarchy")

        # Check that Phase 2 agents are empty
        if hierarchy.get("domain_leads") == {}:
            test_result("Domain Leads empty (Phase 2)", True)
        else:
            test_result("Domain Leads empty (Phase 2)", False)

        if hierarchy.get("executors") == {}:
            test_result("Executors empty (Phase 2)", True)
        else:
            test_result("Executors empty (Phase 2)", False)

    except Exception as e:
        test_result("Agent factory validation", False, str(e))
        traceback.print_exc()

    print()

    # Test 6: PermissionFilter (basic structure check)
    print("### Test Group: PermissionFilter ###")
    try:
        from src.governance.permission_filter import PermissionFilter, GovernanceException

        filter_instance = PermissionFilter()
        test_result("PermissionFilter instantiation", True)

        # Check authorized agents constant
        if hasattr(filter_instance, 'AUTHORIZED_FILE_WRITERS'):
            authorized = filter_instance.AUTHORIZED_FILE_WRITERS
            if "ProjectLeadAgent" in authorized and "DocumentationAgent" in authorized:
                test_result("PermissionFilter has correct authorized agents", True)
            else:
                test_result("PermissionFilter has correct authorized agents", False,
                           f"Expected PL + Doc Agent, got {authorized}")
        else:
            test_result("PermissionFilter has AUTHORIZED_FILE_WRITERS", False)

    except Exception as e:
        test_result("PermissionFilter validation", False, str(e))
        traceback.print_exc()

    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for _, p, _ in test_results if p)
    failed = sum(1 for _, p, _ in test_results if not p)
    total = len(test_results)

    print(f"Total: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if failed > 0:
        print()
        print("Failed Tests:")
        for name, passed, message in test_results:
            if not passed:
                print(f"  - {name}")
                if message:
                    print(f"    {message}")

    return failed == 0


if __name__ == "__main__":
    print()
    success = run_test_suite()
    print()
    sys.exit(0 if success else 1)
