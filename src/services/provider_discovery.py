import os
from typing import List, Dict, Any
from src.config.settings import settings

class ProviderDiscoveryService:
    """
    Discovers available models from API keys and environment variables.
    """
    def __init__(self):
        self.discovered_providers = {}

    async def discover_providers(self) -> Dict[str, List[str]]:
        """
        Discover available providers and their models.
        Returns a dictionary mapping provider names to lists of model names.
        """
        providers = {}

        # 1. Check for Ollama (Local)
        # We assume Ollama is running if OLLAMA_HOST is set or default localhost
        # In a real implementation, we would ping the API
        try:
            # Mock discovery for now, or use a library if available
            # For this MVP, we'll just check env vars and assume standard models
            providers["ollama"] = ["llama3", "mistral", "codellama"]
        except Exception:
            pass

        # 2. Check for OpenAI
        if os.getenv("OPENAI_API_KEY"):
            providers["openai"] = ["gpt-4o", "gpt-3.5-turbo"]

        # 3. Check for Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = ["claude-3-opus", "claude-3-sonnet"]
            
        # 4. Check for LiteLLM (Proxy)
        # If using LiteLLM proxy, we might query its /models endpoint
        if os.getenv("LITELLM_URL"):
             providers["litellm"] = ["all-proxy-models"]

        self.discovered_providers = providers
        return providers

    def get_capabilities(self, model_name: str) -> List[str]:
        """
        Return capabilities for a given model (mocked for now).
        """
        if "gpt-4" in model_name or "claude-3-opus" in model_name:
            return ["reasoning", "coding", "creative"]
        if "llama3" in model_name or "gpt-3.5" in model_name:
            return ["fast", "chat"]
        if "codellama" in model_name:
            return ["coding"]
        return ["general"]
