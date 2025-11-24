"""
Unit tests for AFBaseSettings data contracts (Phase 1 U.B.E.)

Tests Pydantic model validation for:
- TaskDefinition
- StrategicPlan
- ExecutorReport
"""

import pytest
from pydantic import ValidationError
from src.models.data_contracts import TaskDefinition, StrategicPlan, ExecutorReport


class TestTaskDefinition:
    """Unit tests for TaskDefinition model."""
    
    def test_valid_task_definition(self):
        """Test creating a valid TaskDefinition."""
        task = TaskDefinition(
            task_id="task_001",
            domain="Frontend",
            description="Create login component",
            dependencies=["task_000"],
            assigned_to="DevDL"
        )
        
        assert task.task_id == "task_001"
        assert task.domain == "Frontend"
        assert task.description == "Create login component"
        assert task.dependencies == ["task_000"]
        assert task.assigned_to == "DevDL"
    
    def test_task_definition_with_defaults(self):
        """Test TaskDefinition with default values."""
        task = TaskDefinition(
            task_id="task_002",
            domain="Backend",
            description="Implement API endpoint"
        )
        
        assert task.dependencies == []
        assert task.assigned_to is None
    
    def test_task_definition_missing_required_fields(self):
        """Test that TaskDefinition requires task_id, domain, description."""
        with pytest.raises(ValidationError):
            TaskDefinition(task_id="task_003")


class TestStrategicPlan:
    """Unit tests for StrategicPlan model."""
    
    def test_valid_strategic_plan(self):
        """Test creating a valid StrategicPlan."""
        tasks = [
            TaskDefinition(
                task_id="task_001",
                domain="Frontend",
                description="Build UI"
            ),
            TaskDefinition(
                task_id="task_002",
                domain="Backend",
                description="Build API"
            )
        ]
        
        plan = StrategicPlan(
            plan_id="plan_001",
            target_domains=["Frontend", "Backend"],
            tasks=tasks,
            context="User wants a login system",
            metadata={"priority": "high"}
        )
        
        assert plan.plan_id == "plan_001"
        assert len(plan.tasks) == 2
        assert plan.target_domains == ["Frontend", "Backend"]
        assert plan.context == "User wants a login system"
        assert plan.metadata["priority"] == "high"
    
    def test_strategic_plan_with_defaults(self):
        """Test StrategicPlan with default values."""
        plan = StrategicPlan(
            plan_id="plan_002",
            target_domains=["QA"],
            tasks=[]
        )
        
        assert plan.context is None
        assert plan.metadata == {}
    
    def test_strategic_plan_missing_required_fields(self):
        """Test that StrategicPlan requires plan_id, target_domains, tasks."""
        with pytest.raises(ValidationError):
            StrategicPlan(plan_id="plan_003")


class TestExecutorReport:
    """Unit tests for ExecutorReport model."""
    
    def test_valid_executor_report_completed(self):
        """Test creating a valid ExecutorReport with Completed status."""
        report = ExecutorReport(
            executor_task_id="task_001",
            executor_name="CoderExecutor1",
            status="Completed",
            outputs={"file_created": "/app/src/Login.tsx"},
            execution_time_ms=5420
        )
        
        assert report.executor_task_id == "task_001"
        assert report.executor_name == "CoderExecutor1"
        assert report.status == "Completed"
        assert report.outputs["file_created"] == "/app/src/Login.tsx"
        assert report.error_message is None
        assert report.execution_time_ms == 5420
    
    def test_valid_executor_report_failed(self):
        """Test creating a valid ExecutorReport with Failed status."""
        report = ExecutorReport(
            executor_task_id="task_002",
            executor_name="TesterExecutor1",
            status="Failed",
            outputs={},
            error_message="Test suite failed: 3 tests failed"
        )
        
        assert report.status == "Failed"
        assert report.error_message == "Test suite failed: 3 tests failed"
    
    def test_executor_report_with_defaults(self):
        """Test ExecutorReport with default values."""
        report = ExecutorReport(
            executor_task_id="task_003",
            executor_name="WriterExecutor1",
            status="Pending"
        )
        
        assert report.outputs == {}
        assert report.error_message is None
        assert report.execution_time_ms is None
        assert report.metadata == {}
    
    def test_executor_report_invalid_status(self):
        """Test that ExecutorReport only accepts valid status values."""
        with pytest.raises(ValidationError):
            ExecutorReport(
                executor_task_id="task_004",
                executor_name="BadExecutor",
                status="Invalid"  # Not in Literal["Completed", "Failed", "Pending"]
            )
    
    def test_executor_report_missing_required_fields(self):
        """Test that ExecutorReport requires executor_task_id, executor_name, status."""
        with pytest.raises(ValidationError):
            ExecutorReport(executor_task_id="task_005")


class TestDataContractsSerialization:
    """Test serialization/deserialization of data contracts."""
    
    def test_strategic_plan_serialization(self):
        """Test that StrategicPlan can serialize to dict and back."""
        original = StrategicPlan(
            plan_id="plan_001",
            target_domains=["Frontend"],
            tasks=[
                TaskDefinition(
                    task_id="task_001",
                    domain="Frontend",
                    description="Build component"
                )
            ]
        )
        
        # Serialize to dict
        plan_dict = original.dict()
        
        # Deserialize back
        restored = StrategicPlan(**plan_dict)
        
        assert restored.plan_id == original.plan_id
        assert len(restored.tasks) == len(original.tasks)
        assert restored.tasks[0].task_id == original.tasks[0].task_id
    
    def test_executor_report_json_serialization(self):
        """Test that ExecutorReport can serialize to JSON and back."""
        original = ExecutorReport(
            executor_task_id="task_001",
            executor_name="Executor1",
            status="Completed",
            outputs={"result": "success"}
        )
        
        # Serialize to JSON
        json_str = original.json()
        
        # Deserialize back
        restored = ExecutorReport.parse_raw(json_str)
        
        assert restored.executor_task_id == original.executor_task_id
        assert restored.status == original.status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
