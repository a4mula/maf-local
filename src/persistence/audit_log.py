import asyncpg
from datetime import datetime
from src.config.settings import settings
from typing import Optional

class AuditLogProvider:
    """
    Persistence Provider for the Agent Audit Log.
    Uses asyncpg for high-performance, asynchronous PostgreSQL access.
    """

    def __init__(self, db_url: str = settings.DATABASE_URL):
        self.db_url = db_url

    async def _init_db(self):
        """Initializes the audit_log table if it does not exist."""
        conn = None
        try:
            conn = await asyncpg.connect(self.db_url)
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    agent_name VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255),
                    operation VARCHAR(255) NOT NULL,
                    details TEXT
                );
                """
            )
            print("[AuditLog] Audit log table initialized successfully.")
        except Exception as e:
            print(f"[AuditLog] Error initializing database: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def log(
        self,
        agent_name: str,
        operation: str,
        details: str,
        session_id: Optional[str] = None
    ) -> None:
        """Logs an event to the audit_log table."""
        conn = None
        try:
            # Lazy initialize the table on first log attempt if it hasn't been done
            await self._init_db()
            
            conn = await asyncpg.connect(self.db_url)
            await conn.execute(
                """
                INSERT INTO audit_log 
                    (agent_name, session_id, operation, details)
                VALUES 
                    ($1, $2, $3, $4);
                """,
                agent_name,
                session_id,
                operation,
                details,
            )
        except Exception as e:
            # Crucial: Audit logging should not crash the main application
            print(f"[AuditLog] WARNING: Failed to log event for {agent_name} ({operation}). Error: {e}")
        finally:
            if conn:
                await conn.close()


# Example of how to integrate this into src/main.py for demonstration:
async def test_audit_log():
    audit_log = AuditLogProvider()
    print("\n--- Testing AuditLog Provider ---")
    await audit_log.log(
        agent_name="Local-Dev",
        operation="AGENT_STARTUP",
        details="CoreAgent initialization successful with LiteLLM client.",
        session_id="session-xyz-123"
    )
    print("--- AuditLog Test Complete ---")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_audit_log())
