from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar

class AFBaseSettings(BaseSettings):
    """
    Centralized configuration ensuring strict typing and validation.
    Audit Requirement: Declarative Configuration and Canonical Naming.
    """
    # Use SettingsConfigDict for pydantic-settings compatibility
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    # Environment
    ENV: str = "dev"
    
    # --- LLM and LiteLLM Configuration (Cloud/Proxy) ---
    
    # CRITICAL FIX: Use localhost for host-run application to resolve [Errno -3]
    LITELLM_URL: str = "http://localhost:4000"
    
    # REQUIRED SECURITY KEY for LiteLLM
    LITELLM_MASTER_KEY: str = "sk-1234"
    
    # REQUIRED API KEY for Cloud LLMs (Loaded from .env)
    GEMINI_API_KEY: str = "" # Pydantic will load this from .env

    # --- Infrastructure (Host-Run Application Addresses) ---
    # CRITICAL FIX: Use localhost for host-run application
    DATABASE_URL: str = "postgresql://maf_user:maf_pass@localhost:5432/maf_db"
    CHROMA_URL: str = "http://localhost:8000"

    # --- Agent Model Definitions ---
    
    # Local Model (via maf-ollama container)
    OLLAMA_MODEL_NAME: str = "maf-ollama/llama3.1"
    
    # Cloud Model (via LiteLLM proxy)
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"

    # Agent default: Switch to Cloud Model to complete Phase 1
    DEFAULT_MODEL: str = OLLAMA_MODEL_NAME

    # --- AGENT IDENTITY AND PROMPTS (NEW SECTION) ---
    # This serves as the agent's identity and CRITICAL instructions for tool use.
    AGENT_SYSTEM_PROMPT: str = """
You are 'Local-Dev', an AI agent for the Modular Agent Framework (MAF).
Your primary function is to serve the user accurately by using the provided tools.

**CRITICAL INSTRUCTION: When you execute a tool, you MUST use the output
of that tool verbatim for your final answer. Do NOT perform the calculation
or look up the result internally. Do NOT include any narrative about using 
the tool or any 'issues' with the tool. Present the final result cleanly and 
accurately based ONLY on the tool output.**
"""


# Singleton instance
settings = AFBaseSettings()
