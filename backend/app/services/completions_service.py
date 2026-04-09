import asyncio
import logging
import os
from typing import AsyncIterator

from langsmith import traceable
from openai import OpenAI

from app.config import settings

os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
os.environ.setdefault("LANGCHAIN_TRACING_V2", settings.langsmith_tracing_enabled)

logger = logging.getLogger(__name__)


def get_openai_client() -> OpenAI:
    """Get OpenAI client configured for the active LLM provider."""
    return OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_endpoint,
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


def _iter_response_text(stream) -> AsyncIterator[str]:
    """Extract text deltas from Chat Completions stream."""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


async def _sync_stream_completion(client: OpenAI, completion_kwargs: dict):
    """Wrapper to run streaming completion in thread pool."""
    def _sync_call():
        return client.chat.completions.create(**completion_kwargs)
    
    return await asyncio.to_thread(_sync_call)


@traceable(name="stream_chat_completion")
async def stream_chat_completion(
    message_history: list[dict],
    user_id: str,
    thread_id: str,
) -> AsyncIterator[str]:
    """
    Stream chat completion responses using configured LLM provider.
    
    This is a stateless function that takes full message history,
    sends to Chat Completions API, and yields tokens.
    """
    client = get_openai_client()
    api_messages = build_messages_for_api(message_history)
    
    completion_kwargs = {
        "model": settings.llm_model_name,
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
