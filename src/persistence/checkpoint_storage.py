import asyncpg
import json
from typing import List, Optional
from agent_framework import WorkflowCheckpoint
from src.config.settings import settings

class PostgreSQLCheckpointStorage:
    """
    MAF-compliant checkpoint storage using PostgreSQL.
    Implements agent_framework.CheckpointStorage protocol.
    """
    def __init__(self, db_url: str = None):
        self.db_url = db_url or settings.DATABASE_URL

    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        """Save a checkpoint and return its ID."""
        print(f"[Checkpoint] Saving checkpoint {checkpoint.checkpoint_id} for workflow {checkpoint.workflow_id}")
        
        # Serialize to JSON
        data = checkpoint.to_dict()
        serialized_state = json.dumps(data)
        
        conn = await asyncpg.connect(self.db_url)
        try:
            await conn.execute(
                """
                INSERT INTO workflow_checkpoints (checkpoint_id, workflow_id, state, created_at)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (checkpoint_id) DO NOTHING
                """,
                str(checkpoint.checkpoint_id),
                str(checkpoint.workflow_id),
                serialized_state.encode('utf-8') # Store as bytes if column is BYTEA, or string if JSONB/TEXT
            )
            # Note: My migration used BYTEA for state, so encoding is correct.
            return checkpoint.checkpoint_id
        finally:
            await conn.close()

    async def load_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Load a checkpoint by ID."""
        conn = await asyncpg.connect(self.db_url)
        try:
            row = await conn.fetchrow(
                "SELECT state FROM workflow_checkpoints WHERE checkpoint_id = $1",
                str(checkpoint_id)
            )
            if row:
                data = json.loads(row['state'].decode('utf-8'))
                return WorkflowCheckpoint.from_dict(data)
            return None
        finally:
            await conn.close()

    async def list_checkpoint_ids(self, workflow_id: str | None = None) -> List[str]:
        """List checkpoint IDs. If workflow_id is provided, filter by that workflow."""
        conn = await asyncpg.connect(self.db_url)
        try:
            if workflow_id:
                rows = await conn.fetch(
                    "SELECT checkpoint_id FROM workflow_checkpoints WHERE workflow_id = $1 ORDER BY created_at DESC",
                    str(workflow_id)
                )
            else:
                rows = await conn.fetch(
                    "SELECT checkpoint_id FROM workflow_checkpoints ORDER BY created_at DESC"
                )
            return [str(row['checkpoint_id']) for row in rows]
        finally:
            await conn.close()

    async def list_checkpoints(self, workflow_id: str | None = None) -> List[WorkflowCheckpoint]:
        """List checkpoint objects. If workflow_id is provided, filter by that workflow."""
        conn = await asyncpg.connect(self.db_url)
        try:
            if workflow_id:
                rows = await conn.fetch(
                    "SELECT state FROM workflow_checkpoints WHERE workflow_id = $1 ORDER BY created_at DESC",
                    str(workflow_id)
                )
            else:
                rows = await conn.fetch(
                    "SELECT state FROM workflow_checkpoints ORDER BY created_at DESC"
                )
            
            checkpoints = []
            for row in rows:
                data = json.loads(row['state'].decode('utf-8'))
                checkpoints.append(WorkflowCheckpoint.from_dict(data))
            return checkpoints
        finally:
            await conn.close()

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint by ID."""
        conn = await asyncpg.connect(self.db_url)
        try:
            result = await conn.execute(
                "DELETE FROM workflow_checkpoints WHERE checkpoint_id = $1",
                str(checkpoint_id)
            )
            return "DELETE 1" in result
        finally:
            await conn.close()
