import asyncio
import logging
import os
from typing import Iterator
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from langsmith import traceable
from openai import NotFoundError, OpenAI

from app.config import settings

os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)
os.environ.setdefault("LANGCHAIN_TRACING_V2", settings.langsmith_tracing_enabled)

_project_client: AIProjectClient | None = None
_project_credential: DefaultAzureCredential | None = None
_openai_client: OpenAI | None = None
_STREAM_END = object()
logger = logging.getLogger(__name__)


def build_response_tools() -> list[dict]:
    tools: list[dict] = []
    if settings.openai_vector_store_id:
        tools.append(
            {
                "type": "file_search",
                "vector_store_ids": [settings.openai_vector_store_id],
            }
        )
    return tools


def _without_vector_store(kwargs: dict) -> dict:
    fallback = dict(kwargs)
    fallback.pop("tools", None)
    return fallback


def _is_vector_store_not_found(error: Exception) -> bool:
    if not isinstance(error, NotFoundError):
        return False
    try:
        message = error.response.json().get("error", {}).get("message", "")
    except Exception:
        message = str(error)
    return "Vector store" in message and "not found" in message


def normalize_project_endpoint(endpoint: str) -> str:
    raw = endpoint.strip()
    if not raw:
        raise ValueError("AZURE_OPENAI_ENDPOINT is required")

    parsed = urlsplit(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("AZURE_OPENAI_ENDPOINT must be a valid absolute URL")

    normalized = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")).rstrip("/")
    if "/api/projects/" not in normalized:
        raise ValueError(
            "AZURE_OPENAI_ENDPOINT must be an Azure AI Project endpoint containing '/api/projects/{project-name}'"
        )
    return normalized


def get_project_client() -> AIProjectClient:
    global _project_client
    global _project_credential

    if _project_client is None:
        _project_credential = DefaultAzureCredential()
        _project_client = AIProjectClient(
            endpoint=normalize_project_endpoint(settings.azure_openai_endpoint),
            credential=_project_credential,
        )
    return _project_client


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = get_project_client().get_openai_client(
            api_key=settings.azure_openai_api_key,
        )
    return _openai_client


async def _close_project_client() -> None:
    global _project_client
    global _project_credential
    global _openai_client

    if _openai_client is not None:
        await asyncio.to_thread(_openai_client.close)
        _openai_client = None
    if _project_client is not None:
        await asyncio.to_thread(_project_client.close)
        _project_client = None
    if _project_credential is not None:
        await asyncio.to_thread(_project_credential.close)
        _project_credential = None


def _sync_assistant_update(client: OpenAI, assistant_id: str, assistant_kwargs: dict) -> None:
    raise NotImplementedError


def _sync_assistant_create(client: OpenAI, assistant_kwargs: dict):
    raise NotImplementedError


def build_response_input(message_history: list[dict]) -> list[dict]:
    input_items: list[dict] = []
    for message in message_history:
        role = message.get("role")
        content = (message.get("content") or "").strip()
        if role not in {"user", "assistant", "system", "developer"}:
            continue
        if not content:
            continue
        input_items.append(
            {
                "role": role,
                "content": content,
            }
        )
    return input_items


def build_response_kwargs(message_history: list[dict], user_id: str, thread_id: str) -> dict:
    kwargs = {
        "model": settings.azure_openai_deployment_name,
        "input": build_response_input(message_history),
        "instructions": (
            "You are a helpful assistant. Answer questions clearly and concisely "
            "using retrieved documents where relevant. "
            f"User ID: {user_id}. Thread ID: {thread_id}."
        ),
        "store": False,
        "user": user_id,
    }
    tools = build_response_tools()
    if tools:
        kwargs["tools"] = tools
    return kwargs


def _iter_response_text(stream) -> Iterator[str]:
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


def _stream_response(client: OpenAI, response_kwargs: dict):
    return client.responses.stream(**response_kwargs)


def _next_or_stream_end(iterator: Iterator[str]):
    return next(iterator, _STREAM_END)


async def get_or_create_assistant() -> str:
    return "responses-api"


@traceable(name="create_openai_thread")
async def create_openai_thread() -> str:
    return str(uuid4())


@traceable(name="stream_assistant_response")
async def stream_assistant_response(
    message_history: list[dict],
    user_message: str,
    user_id: str,
    thread_id: str,
):
    client = get_openai_client()
    response_kwargs = build_response_kwargs(message_history, user_id, thread_id)
    fallback_kwargs = _without_vector_store(response_kwargs)

    try:
        with await asyncio.to_thread(_stream_response, client, response_kwargs) as stream:
            delta_iter: Iterator[str] = iter(_iter_response_text(stream))
            while True:
                delta = await asyncio.to_thread(_next_or_stream_end, delta_iter)
                if delta is _STREAM_END:
                    break
                yield delta
            await asyncio.to_thread(stream.get_final_response)
    except Exception as exc:
        if not (_is_vector_store_not_found(exc) and settings.openai_vector_store_id):
            raise
        logger.warning(
            "Configured OPENAI_VECTOR_STORE_ID '%s' was not found. Continuing without vector store.",
            settings.openai_vector_store_id,
        )
        with await asyncio.to_thread(_stream_response, client, fallback_kwargs) as stream:
            delta_iter = iter(_iter_response_text(stream))
            while True:
                delta = await asyncio.to_thread(_next_or_stream_end, delta_iter)
                if delta is _STREAM_END:
                    break
                yield delta
            await asyncio.to_thread(stream.get_final_response)
