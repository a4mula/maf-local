from pydantic_settings import BaseSettings, SettingsConfigDict

class AFBaseSettings(BaseSettings):
    """
    Centralized configuration ensuring strict typing and validation.
    Audit Requirement: Declarative Configuration and Canonical Naming.
    """
    # Use SettingsConfigDict for pydantic-settings compatibility
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    # Environment
    ENV: str = "dev"
    
    # LLM and LiteLLM Configuration
    # CRITICAL FIX: Use localhost for host-run application to resolve [Errno -3]
    LITELLM_URL: str = "http://localhost:4000"
    
    # REQUIRED SECURITY KEY
    LITELLM_MASTER_KEY: str = "sk-1234" 
    
    # Infrastructure (Host-Run Application Addresses)
    # CRITICAL FIX: Use localhost for host-run application
    DATABASE_URL: str = "postgresql://maf_user:maf_pass@localhost:5432/maf_db"
    CHROMA_URL: str = "http://localhost:8000"

    # Agent defaults
    DEFAULT_MODEL: str = "maf-default" # Maps to the LiteLLM config alias

# Singleton instance
settings = AFBaseSettings()
