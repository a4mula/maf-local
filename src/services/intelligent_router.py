from typing import List, Optional
from src.services.provider_discovery import ProviderDiscoveryService

class IntelligentRouter:
    """
    Selects the optimal model for a task based on capabilities, cost, and speed.
    Prioritizes FOSS (Free/Open Source) models when possible.
    """
    def __init__(self, discovery_service: ProviderDiscoveryService):
        self.discovery = discovery_service

    async def select_model(
        self,
        task_type: str,
        max_cost: float = 0.0, # Default to free
        min_speed: str = "medium"
    ) -> str:
        """
        Select the best model for the given task constraints.
        """
        providers = await self.discovery.discover_providers()
        
        # Flatten available models
        all_models = []
        for provider, models in providers.items():
            for model in models:
                all_models.append({"name": model, "provider": provider})
        
        # 1. Filter by Task Type / Capabilities
        capable_models = []
        for m in all_models:
            caps = self.discovery.get_capabilities(m["name"])
            # Simple matching logic
            if task_type == "coding" and "coding" in caps:
                capable_models.append(m)
            elif task_type == "reasoning" and "reasoning" in caps:
                capable_models.append(m)
            elif task_type == "general":
                capable_models.append(m)
        
        if not capable_models:
            # Fallback to any model
            capable_models = all_models

        # 2. Filter by Cost (FOSS First)
        # We assume 'ollama' provider is free (FOSS)
        free_models = [m for m in capable_models if m["provider"] == "ollama"]
        
        if free_models:
            # Return the first free model
            # In a real system, we'd sort by speed/quality
            return f"{free_models[0]['provider']}/{free_models[0]['name']}"
            
        # 3. Fallback to Paid
        # If no free models match, check budget
        if max_cost > 0:
            paid_models = [m for m in capable_models if m["provider"] != "ollama"]
            if paid_models:
                return f"{paid_models[0]['provider']}/{paid_models[0]['name']}"
                
        # Default fallback
        return "ollama/llama3" # Safe default
