from agent_framework import ChatAgent
from src.tools.universal_tools import registry
import src.tools.code_tools # Ensure tools are registered
import os

class ProjectLeadAgent:
    """
    Tier 2: Strategic Director
    - Makes high-level technical decisions
    - Delegates to Domain Leads
    """
    def __init__(self, chat_client):
        
        # Dynamic Project Context Loading
        context = ""
        context_paths = [
            "/app/project_root/README.md",
            "/app/project_root/.meta/project_brief.md",
            "/app/project_root/.ai/project_guidelines.md"
        ]
        
        for path in context_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context += f"\n\n# {os.path.basename(path)}\n{content}"
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
        
        # Alternative: Try relative paths
        if not context:
            alt_paths = [
                "README.md",
                ".meta/project_brief.md",
                ".ai/project_guidelines.md"
            ]
            for path in alt_paths:
                try:
                    if os.path.exists(path):
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            context += f"\n\n# {os.path.basename(path)}\n{content}"
                except Exception as e:
                    print(f"Warning: Could not load project context: {e}")

        # Create MAF ChatAgent with tools
        self.sdk_agent = ChatAgent(
            name="ProjectLead",
            instructions=f"Make technical decisions. Create workflows. Delegate to DLs.\n\nCurrent Project Context:{context}",
            tools=registry.get_ai_functions(),  # Use MAF AIFunction objects
            chat_client=chat_client
        )

    async def receive_idea(self, idea: str):
        print(f"[ProjectLead] Received idea: {idea}")
        
        # Use the MAF ChatAgent to process the idea
        # The @use_function_invocation decorator on the client handles tool execution
        from agent_framework import AgentThread
        
        thread = AgentThread()
        response = await self.sdk_agent.run(idea, thread=thread)
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Log the decision (simplified)
        print(f"[ProjectLead] Decision logged: {idea} -> {response_text[:50]}...")
        
        return f"**Project Lead Analysis:**\n\n{response_text}"
