from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str = "gpt-4o-mini"
    azure_openai_api_version: str = "2024-08-01-preview"
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
