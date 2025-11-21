import json
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from agent_framework import ChatAgent
from src.models.decision import Decision
from src.persistence.maf_message_store import PostgreSQLMessageStore
from src.services.drift_detection import detect_drift

class GovernanceAgent:
    """
    Global Agent: Immutable truth storage.
    Stores authoritative decisions and detects drift.
    """
    def __init__(self, db_store: PostgreSQLMessageStore, chat_client):
        self.db = db_store # Reusing the existing store connection logic for now
        self.sdk_agent = ChatAgent(
            name="Governance",
            instructions="Store immutable decisions. Detect drift. Maintain truth.",
            tools=[],
            chat_client=chat_client
        )

    async def store_decision(self, decision: Decision):
        """Store authoritative decision in PostgreSQL"""
        print(f"[Governance] Storing decision: {decision.id} ({decision.category})")
        
        import asyncpg
        conn = await asyncpg.connect(self.db.db_url)
        try:
            await conn.execute(
                """
                INSERT INTO governance_decisions 
                (decision_id, category, content, created_at, created_by, immutable)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                str(decision.id),
                decision.category,
                json.dumps(decision.content),
                decision.created_at,
                decision.created_by,
                decision.immutable
            )
        finally:
            await conn.close()

    async def get_all_decisions(self) -> List[Decision]:
        """Retrieve all authoritative decisions"""
        import asyncpg
        conn = await asyncpg.connect(self.db.db_url)
        try:
            rows = await conn.fetch("SELECT * FROM governance_decisions")
            return [
                Decision(
                    id=row['decision_id'],
                    category=row['category'],
                    content=json.loads(row['content']),
                    created_at=row['created_at'],
                    created_by=row['created_by'],
                    immutable=row['immutable']
                )
                for row in rows
            ]
        finally:
            await conn.close()

    async def check_drift(self, current_state: dict) -> List[str]:
        """Compare current state against authoritative decisions"""
        decisions = await self.get_all_decisions()
        return detect_drift(decisions, current_state)
