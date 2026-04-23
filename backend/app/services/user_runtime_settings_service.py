from __future__ import annotations

from app.db.user_model_settings import get_user_model_settings
from app.services.secret_crypto_service import decrypt_secret


def get_user_runtime_settings(access_token: str, user_id: str, require_complete: bool = True) -> dict:
    row = get_user_model_settings(access_token, user_id)

    if row is None:
        row = {}

    llm_api_key = decrypt_secret(row.get("llm_api_key_encrypted"))
    embedding_api_key = decrypt_secret(row.get("embedding_api_key_encrypted")) or llm_api_key

    resolved = {
        "llm_model_name": (row.get("llm_model_name") or "").strip(),
        "llm_base_url": (row.get("llm_base_url") or "").strip(),
        "llm_api_key": llm_api_key,
        "embedding_model_name": (row.get("embedding_model_name") or "").strip(),
        "embedding_base_url": (row.get("embedding_base_url") or "").strip(),
        "embedding_api_key": embedding_api_key,
        "embedding_dimensions": int((row.get("embedding_dimensions") or 1536)),
    }

    if require_complete:
        if not resolved["llm_model_name"] or not resolved["llm_base_url"] or not resolved["llm_api_key"]:
            raise RuntimeError("User model settings are incomplete. Please configure model settings.")

    return resolved
