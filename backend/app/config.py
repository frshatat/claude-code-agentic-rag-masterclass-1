from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_deployment_name: str = "gpt-4o-mini"
    langsmith_api_key: str = ""
    langsmith_project: str = "agentic-rag-masterclass"
    langsmith_tracing_enabled: str = "true"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
