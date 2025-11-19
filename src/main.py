import asyncio
import sys
import uuid
import httpx
from rich.console import Console
from rich.status import Status

from src.clients.litellm_client import LiteLLMChatClient
from src.agents.core_agent import CoreAgent
from src.persistence.audit_log import AuditLogProvider
from src.persistence.message_store import MessageStoreProvider
from src.config.settings import settings
from src.config.tool_registry import TOOL_REGISTRY 

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

async def main():
    console.print("--- MAF (Local 2025) Initializing ---")
    session_id = str(uuid.uuid4())

    try:
        await wait_for_service(settings.LITELLM_URL, "LiteLLM Proxy")
    except TimeoutError as e:
        console.print(f"[bold red]System Error:[/bold red] {e}")
        sys.exit(1)

    llm_client = LiteLLMChatClient(model_name=settings.DEFAULT_MODEL)
    audit_log = AuditLogProvider()
    message_store = MessageStoreProvider()
    message_store.session_id = session_id

    agent_tools = [t.model_dump() for t in TOOL_REGISTRY.get("Local-Dev", [])]

    agent = CoreAgent(
        name="Local-Dev",
        # STRICT PROMPT: Now safe because CoreAgent handles "Hello" internally.
        system_prompt=(
            "You are a precise AI assistant named Local-Dev. "
            "CRITICAL INSTRUCTION: If a tool is provided to you, you MUST use it to answer questions. "
            "Do not simulate calculations or database queries. "
            "If the user asks for a calculation, use 'execute_code'. "
            "If the user asks for history, use 'query_agent_messages'. "
            "If NO tools are provided, simply chat conversationally."
        ),
        client=llm_client,
        audit_log=audit_log,
        message_store=message_store,
        registered_tools=agent_tools
    )

    await audit_log.log(agent.name, "SESSION_START", f"ID: {session_id}", session_id)

    console.print(f"[System] Agent '[bold yellow]{agent.name}[/bold yellow]' is ready. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ")
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold green]Goodbye![/bold green]")
                break
            
            if not user_input.strip(): continue

            with Status("[bold cyan]Thinking...[/bold cyan]", spinner="dots", console=console):
                response = await agent.process(user_input)

            console.print(f"[bold green]Agent:[/bold green] {response}")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            try: await audit_log.log(agent.name, "ERROR", str(e), session_id)
            except: pass

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit(0)
