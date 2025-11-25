# CoderExecutor API Example

The `CoderExecutor` is a Tier 4 executor responsible for generating code artifacts. Below is a minimal usage example:

```python
from src.agents.executors.coder_executor import CoderExecutor
from src.models.data_contracts import TaskDefinition

# Define a task
task = TaskDefinition(
    task_id="task-001",
    domain="Development",
    description="Implement a utility function to capitalize words",
    dependencies=[],
    assigned_to="DevDomainLead",
)

# Create executor and run
executor = CoderExecutor()
report = executor.execute(task)

print("Executor Report:")
print(report)
```

**Key Points**:
- The executor returns an `ExecutorReport` containing `executor_task_id`, `executor_name`, `status`, `outputs`, and optional metadata.
- Errors are captured in `error_message` and the status will be `Failed` if execution raises an exception.
- This example assumes the surrounding MAF infrastructure (LLM client, logging) is configured.
