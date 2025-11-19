import asyncpg
import json
from typing import List, Dict, Optional
from src.config.settings import settings

async def query_agent_messages(session_id: Optional[str] = None, role: Optional[str] = None) -> str:
    """
    Queries the agent_messages table for conversation history based on provided filters.
    
    Args:
        session_id: Optional: Filter by a specific session ID.
        role: Optional: Filter by message role (user, assistant, or system).

    Returns:
        A JSON string containing the matching message history, or an error message.
    """
    db_url = settings.DATABASE_URL
    conn = None
    
    # 1. Build the SQL query dynamically based on arguments
    sql_base = "SELECT session_id, role, content, timestamp FROM agent_messages"
    conditions = []
    params = []
    
    if session_id:
        conditions.append("session_id = $" + str(len(params) + 1))
        params.append(session_id)
        
    if role:
        conditions.append("role = $" + str(len(params) + 1))
        params.append(role)
        
    if conditions:
        sql_query = sql_base + " WHERE " + " AND ".join(conditions)
    else:
        sql_query = sql_base
        
    # Limit to the most recent 5 entries to prevent overwhelming the context
    sql_query += " ORDER BY timestamp DESC LIMIT 5;" 

    try:
        conn = await asyncpg.connect(db_url)
        records = await conn.fetch(sql_query, *params)
        
        # 2. Format results for the LLM
        results = [
            {
                "session_id": r['session_id'],
                "role": r['role'],
                "content": r['content'],
                # Convert datetime to string for JSON serialization
                "timestamp": r['timestamp'].isoformat() 
            }
            for r in records
        ]
        
        if not results:
            return "No messages found matching the criteria."
            
        # 3. Return as a JSON string
        return json.dumps(results, indent=2)

    except Exception as e:
        return f"Database Tool Error: Failed to execute message query. Details: {e}"
    finally:
        if conn:
            await conn.close()

# Note: While not registered in the ToolRegistry yet, this is a useful sister function.
async def query_audit_log(operation: Optional[str] = None, agent_name: Optional[str] = None) -> str:
    """
    Queries the audit_log table for recent entries based on provided filters.
    """
    db_url = settings.DATABASE_URL
    conn = None
    
    sql_base = "SELECT timestamp, agent_name, operation, details FROM audit_log"
    conditions = []
    params = []
    
    if operation:
        conditions.append("operation = $" + str(len(params) + 1))
        params.append(operation)
        
    if agent_name:
        conditions.append("agent_name = $" + str(len(params) + 1))
        params.append(agent_name)
        
    if conditions:
        sql_query = sql_base + " WHERE " + " AND ".join(conditions)
    else:
        sql_query = sql_base
        
    sql_query += " ORDER BY timestamp DESC LIMIT 5;"

    try:
        conn = await asyncpg.connect(db_url)
        records = await conn.fetch(sql_query, *params)
        
        results = [
            {
                "timestamp": r['timestamp'].isoformat(),
                "agent_name": r['agent_name'],
                "operation": r['operation'],
                "details": r['details']
            }
            for r in records
        ]
        
        if not results:
            return "No audit log entries found matching the criteria."
            
        return json.dumps(results, indent=2)

    except Exception as e:
        return f"Database Tool Error: Failed to execute audit query. Details: {e}"
    finally:
        if conn:
            await conn.close()
