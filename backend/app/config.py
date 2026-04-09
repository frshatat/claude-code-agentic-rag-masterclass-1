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
