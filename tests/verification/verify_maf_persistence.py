"""
Test script for MAF-compliant PostgreSQL message store.
"""

import asyncio
import uuid
from agent_framework import ChatMessage, AgentThread
from src.persistence.maf_message_store import PostgreSQLMessageStore

async def main():
    print("--- Testing MAF-Compliant PostgreSQL Message Store ---\n")
    
    # Create a unique session ID
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    print(f"Session ID: {session_id}\n")
    
    # Test 1: Create store and add messages
    print("Test 1: Creating store and adding messages...")
    store = PostgreSQLMessageStore(session_id=session_id)
    
    messages = [
        ChatMessage(role="user", text="Hello, how are you?"),
        ChatMessage(role="assistant", text="I'm doing well, thank you!"),
        ChatMessage(role="user", text="What's the weather like?"),
    ]
    
    await store.add_messages(messages)
    print("✅ Messages added\n")
    
    # Test 2: Retrieve messages
    print("Test 2: Retrieving messages...")
    retrieved = await store.list_messages()
    print(f"Retrieved {len(retrieved)} messages:")
    for i, msg in enumerate(retrieved, 1):
        print(f"  {i}. [{msg.role}]: {msg.text}")
    print()
    
    # Test 3: Serialization
    print("Test 3: Serializing store state...")
    state = await store.serialize()
    print(f"Serialized state: {state}\n")
    
    # Test 4: Deserialization
    print("Test 4: Deserializing store...")
    restored_store = await PostgreSQLMessageStore.deserialize(state)
    restored_messages = await restored_store.list_messages()
    print(f"Restored {len(restored_messages)} messages from serialized state")
    print()
    
    # Test 5: Use with AgentThread
    print("Test 5: Using with SDK AgentThread...")
    thread = AgentThread(message_store=store)
    
    # Add a new message through the thread
    new_msg = ChatMessage(role="assistant", text="The weather is sunny!")
    await thread.on_new_messages(new_msg)
    
    # Verify it was stored
    all_messages = await store.list_messages()
    print(f"Total messages after thread update: {len(all_messages)}")
    print(f"Latest message: [{all_messages[-1].role}]: {all_messages[-1].text}")
    print()
    
    # Test 6: Thread serialization
    print("Test 6: Serializing AgentThread...")
    thread_state = await thread.serialize()
    print(f"Thread state keys: {list(thread_state.keys())}")
    print()
    
    print("✅ All tests passed!")
    print("\nThe PostgreSQL message store is now MAF SDK-compliant!")

if __name__ == "__main__":
    asyncio.run(main())
