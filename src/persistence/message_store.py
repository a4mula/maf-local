import asyncpg
from typing import List, Dict
from src.config.settings import settings
from datetime import datetime
from src.utils import get_logger

logger = get_logger(__name__)

# Define the expected structure for a message in the history
Message = Dict[str, str]

class MessageStoreProvider:
    """
    Persistence Provider for storing and retrieving Agent conversation history.
    Uses asyncpg for high-performance, asynchronous PostgreSQL access.
    """

    def __init__(self, db_url: str = settings.DATABASE_URL):
        self.db_url = db_url
        self.session_id: str = "default_session" # Placeholder, will be set by AgentFactory

    async def _init_db(self):
        """Initializes the agent_messages table if it does not exist."""
        conn = None
        try:
            conn = await asyncpg.connect(self.db_url)
            # Table to store individual messages
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_messages (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
                    content TEXT
                );
                """
            )
        except Exception as e:
            logger.info(f"[MessageStore] Error initializing database: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def store_message(self, role: str, content: str) -> None:
        """Stores a single message associated with the current session."""
        conn = None
        try:
            # Ensure the table is ready
            await self._init_db()
            
            conn = await asyncpg.connect(self.db_url)
            await conn.execute(
                """
                INSERT INTO agent_messages 
                    (session_id, role, content)
                VALUES 
                    ($1, $2, $3);
                """,
                self.session_id,
                role,
                content,
            )
        except Exception as e:
            # Crucial: Message storage failure should be logged but not crash the app
            logger.info(f"[MessageStore] WARNING: Failed to store message for session {self.session_id}. Error: {e}")
        finally:
            if conn:
                await conn.close()

    async def get_history(self, limit: int = 20) -> List[Message]:
        """Retrieves the message history for the current session, up to a limit."""
        conn = None
        try:
            await self._init_db()

            conn = await asyncpg.connect(self.db_url)
            records = await conn.fetch(
                """
                SELECT role, content 
                FROM agent_messages
                WHERE session_id = $1
                ORDER BY timestamp ASC
                LIMIT $2;
                """,
                self.session_id,
                limit,
            )
            # Convert asyncpg records into the standard LLM message format
            return [{"role": r['role'], "content": r['content']} for r in records]
        except Exception as e:
            logger.info(f"[MessageStore] WARNING: Failed to retrieve history for session {self.session_id}. Error: {e}")
            return []
        finally:
            if conn:
                await conn.close()
