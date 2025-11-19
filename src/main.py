import asyncio
import sys
import uuid 
import httpx 
from rich.console import Console # NEW: For rich terminal output
from rich.status import Status    # NEW: For the activity spinner

from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.settings import settings

# Initialize a Rich console globally
console = Console() # NEW

# ... (wait_for_service function remains unchanged) ...
async def wait_for_service(url: str, description: str, timeout: int = 60, interval: int = 5):
    """Waits for a service at the given URL to become available."""
    print(f"[System] Waiting for {description} at {url}...")
    for elapsed in range(0, timeout, interval):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=interval)
                if response.status_code < 500:
                    print(f"[System] {description} is ready.")
                    return
        except httpx.RequestError:
            pass

        print(f"[System] {description} not ready. Retrying in {interval}s... ({elapsed + interval}s elapsed)")
        await asyncio.sleep(interval)

    raise TimeoutError(f"Service {description} at {url} failed to become available within {timeout} seconds.")
# ----------------------------------------------------


async def main():
    print("--- MAF (Local 2025) Initializing ---")

    # 0. SETUP SESSION
    session_id = str(uuid.uuid4())
    print(f"[System] Starting new session: {session_id}")

    # 1. DEPENDENCY INJECTION (DI) SETUP
    
    # CRITICAL FIX: Ensure LiteLLM is ready before attempting to initialize the client.
    try:
        await wait_for_service(
            url=settings.LITELLM_URL,
            description="LiteLLM Proxy"
        )
    except TimeoutError as e:
        print(f"[System Error] Initialization failed: {e}")
        sys.exit(1)


    print("[System] Initializing LiteLLM Client...")
    llm_client = LiteLLMChatClient()
    
    # Initialize Persistence Providers
    print("[System] Initializing Persistence Providers...")
    audit_log_provider = AuditLogProvider()
    message_store_provider = MessageStoreProvider()
    
    # CRITICAL: Set the current session ID on the message store
    message_store_provider.session_id = session_id
    
    # 2. AGENT ASSEMBLY
    print("[System] Assembling 'Ollama-Agent' with persistence providers...")
    agent = CoreAgent(
        name="Local-Dev",
        # NOTE: This system_prompt is a temporary hardcoded fix for the LLM's math error. 
        # It MUST be cleaned up in the next phase to follow DI principles.
        system_prompt="You are a helpful AI assistant running locally on an RTX 3060 Ti.",
        client=llm_client,
        audit_log=audit_log_provider,       # Inject Audit Log
        message_store=message_store_provider # Inject Message Store
    )
    
    # Initial audit log entry
    await audit_log_provider.log(
        agent_name=agent.name,
        operation="SESSION_START",
        details=f"New agent session started with session_id: {session_id}",
        session_id=session_id
    )

    # NEW: Flag to track the first (slow) interaction
    first_interaction = True

    # 3. RUNTIME LOOP
    print(f"[System] Agent '{agent.name}' is ready. Type 'exit' to quit.")
    while True:
        try:
            # Use console.input instead of built-in input for better rich compatibility
            user_input = console.input("[bold yellow]You:[/bold yellow] ")
            
            if user_input.lower() in ["exit", "quit"]:
                await audit_log_provider.log(
                    agent_name=agent.name,
                    operation="SESSION_END",
                    details="User initiated exit.",
                    session_id=session_id
                )
                break
                
            # Define status message
            if first_interaction:
                status_text = "[bold cyan]Agent: Loading LLM model for first time... please wait[/bold cyan]"
            else:
                status_text = "[bold cyan]Agent: Thinking...[/bold cyan]"

            # Run the agent processing inside the rich status spinner
            with Status(status_text, spinner="dots", console=console):
                response = await agent.process(user_input)

            # Print the final response and update the flag
            console.print(f"[bold green]Agent:[/bold green] {response}")
            first_interaction = False

        except Exception as e:
            # Removed the `print("Agent: ... thinking ...")` since rich handles it
            print(f"[System Error] An error occurred during processing: {e}")
            await audit_log_provider.log(
                agent_name=agent.name,
                operation="CRITICAL_ERROR",
                details=f"An unhandled exception occurred: {str(e)}",
                session_id=session_id
            )
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
