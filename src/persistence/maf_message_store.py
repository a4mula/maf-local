"""
PostgreSQL-backed ChatMessageStore for Microsoft Agent Framework

Direct implementation of ChatMessageStoreProtocol using PostgreSQL,
replacing the custom MessageStoreProvider with MAF SDK-native persistence.
"""

import asyncpg
from typing import Sequence, MutableMapping, Any
from agent_framework import ChatMessage
from agent_framework._threads import ChatMessageStoreProtocol
from src.config.settings import settings
from src.utils import get_logger

logger = get_logger(__name__)


class PostgreSQLMessageStore(ChatMessageStoreProtocol):
    """
    MAF SDK-native message store backed by PostgreSQL.
    
    This is a direct implementation of ChatMessageStoreProtocol,
    not a wrapper. It manages conversation persistence using PostgreSQL
    while conforming to the MAF SDK's thread management system.
    """
    
    def __init__(self, session_id: str, db_url: str = None):
        """
        Initialize the PostgreSQL message store.
        
        Args:
            session_id: Unique identifier for this conversation thread
            db_url: Optional database URL (uses settings default if not provided)
        """
        self.session_id = session_id
        self.db_url = db_url or settings.DATABASE_URL
        self._messages_cache: list[ChatMessage] = []
        self._cache_loaded = False
    
    async def _init_db(self):
        """Initialize the agent_messages table if it doesn't exist."""
        conn = None
        try:
            conn = await asyncpg.connect(self.db_url)
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_messages (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    role VARCHAR(50) NOT NULL,
                    content TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_session_timestamp 
                ON agent_messages(session_id, timestamp);
                """
            )
        except Exception as e:
            logger.error(f"[PostgreSQLMessageStore] Error initializing database: {e}")
            raise
        finally:
            if conn:
                await conn.close()
    
    async def list_messages(self) -> list[ChatMessage]:
        """
        Get all messages from PostgreSQL in chronological order.
        
        Returns:
            List of ChatMessage objects from oldest to newest
        """
        conn = None
        try:
            await self._init_db()
            
            conn = await asyncpg.connect(self.db_url)
            records = await conn.fetch(
                """
                SELECT role, content 
                FROM agent_messages
                WHERE session_id = $1
                ORDER BY timestamp ASC;
                """,
                self.session_id
            )
            
            # Convert to SDK ChatMessage format
            messages = []
            for record in records:
                messages.append(
                    ChatMessage(role=record['role'], text=record['content'])
                )
            
            # Update cache
            self._messages_cache = messages
            self._cache_loaded = True
            
            return messages
            
        except Exception as e:
            logger.info(f"[PostgreSQLMessageStore] Error retrieving messages: {e}")
            return []
        finally:
            if conn:
                await conn.close()
    
    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        """
        Add messages to PostgreSQL.
        
        Args:
            messages: Sequence of ChatMessage objects to store
        """
        conn = None
        try:
            await self._init_db()
            
            conn = await asyncpg.connect(self.db_url)
            
            for msg in messages:
                # Extract text content
                content = msg.text if hasattr(msg, 'text') else str(msg.content)
                
                # Extract role (handle both string and enum)
                role = str(msg.role.value) if hasattr(msg.role, 'value') else str(msg.role)
                
                await conn.execute(
                    """
                    INSERT INTO agent_messages (session_id, role, content)
                    VALUES ($1, $2, $3);
                    """,
                    self.session_id,
                    role,
                    content
                )
                
                # Update cache
                self._messages_cache.append(msg)
                
        except Exception as e:
            logger.info(f"[PostgreSQLMessageStore] Error storing messages: {e}")
        finally:
            if conn:
                await conn.close()
    
    @classmethod
    async def deserialize(
        cls, 
        serialized_store_state: MutableMapping[str, Any], 
        **kwargs: Any
    ) -> "PostgreSQLMessageStore":
        """
        Create a new store instance from serialized state.
        
        Args:
            serialized_store_state: Previously serialized state containing session_id
            **kwargs: Additional arguments (db_url, etc.)
            
        Returns:
            New PostgreSQLMessageStore instance
        """
        session_id = serialized_store_state.get("session_id")
        db_url = kwargs.get("db_url")
        
        if not session_id:
            raise ValueError("session_id is required in serialized state")
        
        return cls(session_id=session_id, db_url=db_url)
    
    async def update_from_state(
        self, 
        serialized_store_state: MutableMapping[str, Any], 
        **kwargs: Any
    ) -> None:
        """
        Update the current store instance from serialized state.
        
        Args:
            serialized_store_state: Previously serialized state
            **kwargs: Additional arguments
        """
        # For PostgreSQL backend, messages are already in the database
        # Just update session_id if it changed
        if "session_id" in serialized_store_state:
            new_session_id = serialized_store_state["session_id"]
            if new_session_id != self.session_id:
                self.session_id = new_session_id
                self._cache_loaded = False
                self._messages_cache = []
    
    async def serialize(self, **kwargs: Any) -> dict[str, Any]:
        """
        Serialize the current store state.
        
        The SDK expects a "messages" key with the list of messages.
        We fetch current messages from PostgreSQL.
        
        Returns:
            Serialized state containing messages and metadata
        """
        # Get current messages from database
        messages = await self.list_messages()
        
        # Convert to dict format for serialization
        messages_dict = [msg.to_dict() for msg in messages]
        
        return {
            "messages": messages_dict,
            "session_id": self.session_id,
            "store_type": "postgresql"
        }
