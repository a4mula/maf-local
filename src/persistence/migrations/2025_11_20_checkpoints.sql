-- Workflow checkpoints table
CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    checkpoint_id UUID PRIMARY KEY,
    workflow_id VARCHAR(100),
    state BYTEA,          -- Serialized MAF WorkflowState (pickled or JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_workflow_id 
ON workflow_checkpoints(workflow_id);
