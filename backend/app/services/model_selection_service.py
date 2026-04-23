from __future__ import annotations

from threading import RLock

from app.config import settings


_user_model_overrides: dict[str, dict[str, str]] = {}
_lock = RLock()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def get_available_chat_models() -> list[str]:
    configured = _split_csv(settings.available_models)
    if configured:
        return configured
    return [settings.llm_model_name]


def get_available_embedding_models() -> list[str]:
    configured = _split_csv(settings.available_embedding_models)
    if configured:
        return configured
    return [settings.embedding_model_name]


def get_active_models_for_user(user_id: str) -> dict[str, str]:
    defaults = {
        "chat_model": settings.llm_model_name,
        "embedding_model": settings.embedding_model_name,
    }
    with _lock:
        current = _user_model_overrides.get(user_id, {})
        return {
            "chat_model": current.get("chat_model", defaults["chat_model"]),
            "embedding_model": current.get("embedding_model", defaults["embedding_model"]),
        }


def set_active_models_for_user(
    user_id: str,
    *,
    chat_model: str | None = None,
    embedding_model: str | None = None,
) -> dict[str, str]:
    allowed_chat = set(get_available_chat_models())
    allowed_embedding = set(get_available_embedding_models())

    updates: dict[str, str] = {}
    if chat_model is not None:
        if chat_model not in allowed_chat:
            raise ValueError("Unsupported chat model")
        updates["chat_model"] = chat_model

    if embedding_model is not None:
        if embedding_model not in allowed_embedding:
            raise ValueError("Unsupported embedding model")
        updates["embedding_model"] = embedding_model

    with _lock:
        if user_id not in _user_model_overrides:
            _user_model_overrides[user_id] = {}
        _user_model_overrides[user_id].update(updates)

    return get_active_models_for_user(user_id)
