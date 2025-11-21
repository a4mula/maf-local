import asyncio
import sys
import uuid
import httpx
from rich.console import Console
from rich.status import Status

from src.clients.litellm_client import LiteLLMChatClient
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.settings import settings
from src.services.agent_factory import AgentFactory

# Ensure tools are registered
import src.tools.code_tools 

console = Console()

async def wait_for_service(url: str, description: str, timeout: int = 60, interval: int = 5):
    console.print(f"[System] Waiting for {description} at {url}...")
    for elapsed in range(0, timeout, interval):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=interval)
                if response.status_code < 500:
                    console.print(f"[System] {description} is ready.")
                    return
        except httpx.RequestError:
            pass
        console.print(f"[System] {description} not ready. Retrying...")
        await asyncio.sleep(interval)
    raise TimeoutError(f"Service {description} failed.")

async def run_api_server(hierarchy):
    """Run the FastAPI server in the background."""
    import uvicorn
    from src.api.agent_api import app, set_agent_hierarchy
    
    # Inject the agent hierarchy into the API
    set_agent_hierarchy(hierarchy)
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8002, log_level="info")
    server = uvicorn.Server(config)
    console.print("[System] Starting API server on http://0.0.0.0:8002")
    await server.serve()

async def run_interactive_mode(liaison, audit_log, session_id):
    """Run the interactive terminal mode."""
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("[System] You are now talking to the [bold yellow]Liaison Agent[/bold yellow].")
    console.print("[System] Type 'exit' to quit.")
    
    while True:
        try:
            user_input = await asyncio.get_event_loop().run_in_executor(
                None, console.input, "\n[bold blue]You:[/bold blue] "
            )
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold green]Goodbye![/bold green]")
                break
            
            if not user_input.strip(): continue

            with Status("[bold cyan]Liaison is processing...[/bold cyan]", spinner="dots", console=console):
                # Route through Liaison Agent
                response = await liaison.handle_user_message(user_input)

            console.print(f"[bold green]Liaison:[/bold green] {response}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            try: await audit_log.log("System", "ERROR", str(e), session_id)
            except: pass

async def main():
    console.print("--- Hierarchical MAF Studio (2025) Initializing ---")
    session_id = str(uuid.uuid4())

    try:
        await wait_for_service(settings.LITELLM_URL, "LiteLLM Proxy")
    except TimeoutError as e:
        console.print(f"[bold red]System Error:[/bold red] {e}")
        sys.exit(1)

    audit_log = AuditLogProvider()
    message_store = MessageStoreProvider()
    message_store.session_id = session_id

    # Start Prometheus Metrics Server
    from src.services.metrics_service import MetricsService
    MetricsService().start_server(8001)

    # Initialize the Agent Hierarchy
    console.print("[System] Initializing Agent Hierarchy...")
    hierarchy = AgentFactory.create_hierarchy(message_store=message_store)
    
    liaison = hierarchy["liaison"]
    project_lead = hierarchy["project_lead"]
    
    # Log startup
    await audit_log.log("System", "SESSION_START", f"ID: {session_id}", session_id)

    console.print(f"[System] [bold green]Hierarchical MAF Studio is ready.[/bold green]")
    console.print(f"[System] Active Agents: Liaison, ProjectLead, DomainLeads (Dev/QA/Docs), Executors, Governance, Context, ArtifactManager")
    
    # Run both API server and interactive mode concurrently
    await asyncio.gather(
        run_api_server(hierarchy),
        run_interactive_mode(liaison, audit_log, session_id)
    )

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit(0)

