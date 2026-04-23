from __future__ import annotations

import asyncio
from openai import OpenAI

from app.services.user_runtime_settings_service import get_user_runtime_settings


def get_embedding_client(*, api_key: str, base_url: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


async def embed_texts_for_user(
    access_token: str,
    user_id: str,
    texts: list[str],
) -> list[list[float]]:
    """Embed text chunks with the active embedding model for a user."""
    if not texts:
        return []

    runtime_settings = get_user_runtime_settings(access_token, user_id)
    model_name = runtime_settings["embedding_model_name"]
    client = get_embedding_client(
        api_key=runtime_settings["embedding_api_key"],
        base_url=runtime_settings["embedding_base_url"],
    )

    def _sync_call() -> list[list[float]]:
        response = client.embeddings.create(
            model=model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]

    return await asyncio.to_thread(_sync_call)
