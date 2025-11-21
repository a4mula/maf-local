from src.workflows.main_orchestrator import WorkflowGraph, WorkflowContext
from src.agents.core_agent import CoreAgent

def build_research_workflow(agent: CoreAgent) -> WorkflowGraph:
    """
    Builds a Research Workflow using the provided agent.
    
    Flow:
    1. Research: The agent researches the topic.
    2. Summarize: The agent summarizes the research.
    """
    
    async def research_step(context: WorkflowContext) -> dict:
        topic = context.get("topic")
        print(f"\n[Workflow] Step 1: Researching '{topic}'...")
        
        prompt = f"Please research the following topic and provide key facts: {topic}"
        response = await agent.process(prompt)
        
        return {"research_output": response}

    async def summarize_step(context: WorkflowContext) -> dict:
        research_output = context.get("research_output")
        print(f"\n[Workflow] Step 2: Summarizing findings...")
        
        prompt = f"Here is some research data:\n{research_output}\n\nPlease provide a concise summary of this information."
        response = await agent.process(prompt)
        
        return {"final_summary": response}

    # Build the Graph
    graph = WorkflowGraph()
    
    graph.add_node("Research", research_step)
    graph.add_node("Summarize", summarize_step)
    
    # Linear flow: Research -> Summarize
    graph.add_edge("Research", "Summarize")
    
    return graph
