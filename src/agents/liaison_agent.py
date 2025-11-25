from agent_framework import ChatAgent
from src.agents.project_lead_agent import ProjectLeadAgent
from src.utils import get_logger

logger = get_logger(__name__)

class LiaisonAgent:
    """
    Tier 1: User interface layer
    - Captures user intent
    - No technical decisions
    - Hands off to Project Lead
    """
    def __init__(self, project_lead: ProjectLeadAgent, chat_client):
        self.project_lead = project_lead
        
        logger.debug("LiaisonAgent initializing...")
        
        # Dynamic Project Context Loading
        context = ""
        project_root = "/app/project_root"
        
        try:
            import os
            
            if os.path.exists(project_root):
                logger.debug(f"Scanning project root at {project_root}")
                
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
                    logger.debug("Found README.md")
                    with open(readme_path, "r") as f:
                        context += f"\n\nProject README:\n{f.read()}"
                else:
                    logger.debug("No README.md found in project root")
                    
            else:
                logger.warning(f"Project root not found at {project_root}")
                
        except Exception as e:
            logger.warning(f"Could not load project context: {e}")
            import traceback
            traceback.print_exc()

        logger.debug(f"Context length: {len(context)}")
        self.context = context
        
        self.sdk_agent = ChatAgent(
            name="Liaison",
            instructions=f"Capture user intent. Ask clarifying questions. No technical decisions. Once intent is clear, forward to Project Lead.\n\nCurrent Project Context:{context}",
            tools=[],  # No tools, just conversation
            chat_client=chat_client
        )

    async def handle_user_message(self, message: str):
        """
        Process user message through the Liaison Agent.
        The Liaison determines if the intent is clear enough to forward,
        or if clarifying questions are needed.
        """
        try:
            # Use the SDK agent to process the message
            from agent_framework import ChatMessage, AgentThread
            
            # 1. Classify intent using a temporary thread
            temp_thread = AgentThread()
            classification_prompt = f"""
            Analyze the following user message and classify its intent.
            User Message: "{message}"
            
            Is this message:
            1. A QUESTION about the project, the system, or the agent itself? (e.g. "What is this project?", "Who are you?")
            2. A PROJECT IDEA or instruction to start work? (e.g. "Let's build a game", "Create a new workflow")
            3. GREETING or CHIT-CHAT? (e.g. "Hello", "How are you?")
            
            Respond with ONLY one word: QUESTION, IDEA, or CHIT_CHAT.
            """
            
            classification = await self.sdk_agent.run(classification_prompt, thread=temp_thread)
            intent = str(classification).strip().upper()
            logger.debug(f"User intent classified as: {intent}")
            
            if "IDEA" in intent:
                # Forward to Project Lead
                pl_response = await self.project_lead.receive_idea(message)
                return f"I've forwarded your idea to the Project Lead.\n\n{pl_response}"
            else:
                # Handle locally (Questions, Chit-chat)
                # Use a new thread for the actual conversation to avoid context pollution
                response_thread = AgentThread()
                
                # Explicitly include context in the prompt to ensure awareness
                augmented_prompt = f"""
                Using the following Project Context, answer the user's question.
                
                Project Context:
                {self.context}
                
                User Question: "{message}"
                """
                
                response = await self.sdk_agent.run(augmented_prompt, thread=response_thread)
                return str(response)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error in Liaison Agent: {str(e)}"
