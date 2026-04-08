import asyncio
import os

from langsmith import traceable
from openai import AsyncAzureOpenAI

from app.config import settings

os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
os.environ.setdefault("LANGCHAIN_TRACING_V2", settings.langsmith_tracing_enabled)

_openai_client: AsyncAzureOpenAI | None = None

ASSISTANT_ID_KEY = "OPENAI_ASSISTANT_ID"


def get_openai_client() -> AsyncAzureOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version="2024-08-01-preview",
            azure_endpoint=settings.azure_openai_endpoint,
        )
    return _openai_client


async def get_or_create_assistant() -> str:
    assistant_id = os.environ.get(ASSISTANT_ID_KEY)
    if assistant_id:
        return assistant_id
    client = get_openai_client()
    assistant = await client.beta.assistants.create(
        name="RAG Assistant",
        model=settings.azure_openai_deployment_name,
        tools=[{"type": "file_search"}],
        instructions=(
            "You are a helpful assistant. Answer questions clearly and concisely "
            "using the provided files where relevant."
        ),
    )
    os.environ[ASSISTANT_ID_KEY] = assistant.id
    return assistant.id


@traceable(name="create_openai_thread")
async def create_openai_thread() -> str:
    client = get_openai_client()
    thread = await client.beta.threads.create()
    return thread.id


@traceable(name="stream_assistant_response")
async def stream_assistant_response(
    openai_thread_id: str,
    user_message: str,
    user_id: str,
    thread_id: str,
):
    client = get_openai_client()
    assistant_id = await get_or_create_assistant()

    await client.beta.threads.messages.create(
        thread_id=openai_thread_id,
        role="user",
        content=user_message,
    )

    async with client.beta.threads.runs.stream(
        thread_id=openai_thread_id,
        assistant_id=assistant_id,
        additional_instructions=f"User ID: {user_id}, Thread ID: {thread_id}",
    ) as stream:
        async for delta in stream.text_deltas:
            yield delta
        # Ensure the run is fully done before returning
        await stream.get_final_run()
