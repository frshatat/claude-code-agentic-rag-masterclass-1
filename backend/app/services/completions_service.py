import asyncio
import logging
import os
from typing import AsyncIterator

from langsmith import traceable
from openai import OpenAI

from app.config import settings
from app.services.user_runtime_settings_service import get_user_runtime_settings

os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
os.environ.setdefault("LANGCHAIN_TRACING_V2", settings.langsmith_tracing_enabled)

logger = logging.getLogger(__name__)


def get_openai_client(*, api_key: str, base_url: str) -> OpenAI:
    """Get OpenAI client configured for the active user's LLM settings."""
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def build_messages_for_api(message_history: list[dict]) -> list[dict]:
    """Convert message history to Chat Completions API format."""
    messages = []
    for msg in message_history:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()

        if role not in {"user", "assistant", "system", "developer"}:
            continue
        if not content:
            continue

        messages.append({"role": role, "content": content})

    return messages


@traceable(name="stream_chat_completion")
async def stream_chat_completion(
    message_history: list[dict],
    access_token: str,
    user_id: str,
    thread_id: str,
) -> AsyncIterator[str]:
    """
    Stream chat completion responses using the authenticated user's runtime settings.
    """
    runtime_settings = get_user_runtime_settings(access_token, user_id)
    client = get_openai_client(
        api_key=runtime_settings["llm_api_key"],
        base_url=runtime_settings["llm_base_url"],
    )
    api_messages = build_messages_for_api(message_history)
    chat_model = runtime_settings["llm_model_name"]

    completion_kwargs = {
        "model": chat_model,
        "messages": api_messages,
        "stream": True,
        "user": user_id,
    }

    try:
        with await asyncio.to_thread(client.chat.completions.create, **completion_kwargs) as stream:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
    except Exception:
        logger.exception("Failed during chat completion streaming")
        raise
