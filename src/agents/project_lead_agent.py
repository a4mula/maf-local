from agent_framework import ChatAgent
from src.agents.governance_agent import GovernanceAgent
from src.tools.universal_tools import registry
import os

class ProjectLeadAgent:
    """
    Tier 2: Technical decision-maker
    - Creates MAF Workflow graphs
    - Delegates to Domain Leads
    - Updates Governance Agent with decisions
    """
    def __init__(self, governance_agent: GovernanceAgent, chat_client):
        self.governance = governance_agent
        
        # Dynamic Project Context Loading
        context = ""
        project_root = "/app/project_root"
        
        try:
            
            if os.path.exists(project_root):
                # 1. Generate File Tree (max depth 2 to avoid noise)
                tree_str = "Project Structure:\n"
                for root, dirs, files in os.walk(project_root):
                    # Skip hidden directories and __pycache__
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                    
                    level = root.replace(project_root, '').count(os.sep)
                    if level > 2: continue
                    
                    indent = ' ' * 4 * (level)
                    tree_str += f"{indent}{os.path.basename(root)}/\n"
                    subindent = ' ' * 4 * (level + 1)
                    for f in files:
                        if not f.startswith('.'):
                            tree_str += f"{subindent}{f}\n"
                
                context += f"\n\n{tree_str}"
                
                # 2. Load README.md if it exists
                readme_path = os.path.join(project_root, "README.md")
                if os.path.exists(readme_path):
                    with open(readme_path, "r") as f:
                        context += f"\n\nProject README:\n{f.read()}"
                    
        except Exception as e:
            print(f"Warning: Could not load project context: {e}")

        self.sdk_agent = ChatAgent(
            name="ProjectLead",
            instructions=f"Make technical decisions. Create workflows. Delegate to DLs.\n\nCurrent Project Context:{context}",
            tools=[], # Will add tools later
            chat_client=chat_client
        )

    async def receive_idea(self, idea: str):
        print(f"[ProjectLead] Received idea: {idea}")
        
        # Use the SDK agent to generate an intelligent response
        from agent_framework import ChatMessage, AgentThread
        
        # Create a thread for this conversation
        thread = AgentThread()
        
        # Craft a prompt for the Project Lead to analyze the idea
        prompt = f"""
You are the Project Lead for a hierarchical multi-agent development studio.
A user has submitted the following idea:

"{idea}"

Your job is to:
1. Acknowledge the idea
2. Ask any clarifying questions if needed
3. Provide a high-level technical approach
4. Outline next steps

Be concise but thorough. If the idea is vague, ask specific questions.
"""
        
        # Run the SDK agent
        response = await self.sdk_agent.run(prompt, thread=thread)
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Create a decision record
        from src.models.decision import Decision
        decision = Decision(
            category="vision",
            content={"idea": idea, "initial_analysis": response_text},
            created_by="ProjectLead"
        )
        
        # Store it
        await self.governance.store_decision(decision)
        
        return f"**Project Lead Analysis:**\n\n{response_text}\n\n*Decision stored: {decision.id}*"
