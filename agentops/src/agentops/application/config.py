from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Configuration with safe local defaults.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    agentops_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Persistence
    database_url: str = Field(default="sqlite:///agentops.db")

    # Retrieval
    qdrant_location: str = Field(default=":memory:")

    # Safety
    require_human_approval_tier: int = Field(default=2)

    # Models
    # Use deterministic fakes by default to run without API keys
    use_fake_model: bool = Field(default=True)
    openai_api_key: str | None = Field(default=None)
    gemini_api_key: str | None = Field(default=None)


# Singleton instance
settings = Settings()
