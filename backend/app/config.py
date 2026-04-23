from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    llm_provider: str = "openrouter"
    llm_api_endpoint: str
    llm_api_key: str
    llm_model_name: str = "anthropic/claude-3.5-sonnet"
    available_models: str = ""
    embedding_api_endpoint: str = ""
    embedding_api_key: str = ""
    embedding_model_name: str = "text-embedding-3-small"
    available_embedding_models: str = ""
    secrets_encryption_key: str = Field(default="", validation_alias="SETTINGS_ENCRYPTION_KEY")
    langsmith_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY"),
    )
    langsmith_project: str = Field(
        default="agentic-rag-masterclass",
        validation_alias=AliasChoices("LANGSMITH_PROJECT", "LANGCHAIN_PROJECT"),
    )
    langsmith_tracing_enabled: str = Field(
        default="true",
        validation_alias=AliasChoices("LANGSMITH_TRACING_ENABLED", "LANGCHAIN_TRACING_V2"),
    )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
