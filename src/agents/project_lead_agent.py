from agent_framework import ChatAgent
from src.tools import ALL_TOOLS
import os

class ProjectLeadAgent(ChatAgent):
    """
    Tier 2: Strategic Director (MAF-Compliant)
    - Makes high-level technical decisions
    - Delegates to Domain Leads
    - Outputs STRATEGIC PLANS (StrategicPlan AFBaseSettings model)
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

        # Initialize MAF ChatAgent via inheritance (CRITICAL FIX)
        super().__init__(
            name="ProjectLead",
            instructions=f"""You are the Project Lead. You output STRATEGIC PLANS.

Your responsibilities:
- Make high-level technical decisions
- Break down user requests into strategic plans
- Delegate to Domain Leads (when OLB is implemented)
- Query DocumentationAgent for context before planning

Current Project Context:{context}""",
            tools=ALL_TOOLS,  # Direct tool list - MAF compliant
            chat_client=chat_client
        )

    async def receive_idea(self, idea: str):
        """Process user idea and return strategic plan.
        
        This method will eventually:
        1. Query DocumentationAgent for relevant context (A2A)
        2. Generate StrategicPlan (typed output)
        3. Submit to OLB for routing to Domain Leads
        
        For now (Phase 1): Returns direct LLM response via ChatAgent.run()
        """
        print(f"[ProjectLead] Received idea: {idea}")
        
        # Use inherited ChatAgent.run() method
        # The @use_function_invocation decorator on the client handles tool execution automatically
        from agent_framework import AgentThread
        
        thread = AgentThread()
        response = await self.run(idea, thread=thread)  # Use inherited run() method
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Log the decision (simplified)
        print(f"[ProjectLead] Decision logged: {idea} -> {response_text[:50]}...")
        
        return f"**Project Lead Analysis:**\n\n{response_text}"
