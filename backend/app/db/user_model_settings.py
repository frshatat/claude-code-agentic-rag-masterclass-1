from __future__ import annotations

from app.db.supabase import get_supabase_for_token


TABLE_NAME = "user_model_settings"


def get_user_model_settings(access_token: str, user_id: str) -> dict | None:
    client = get_supabase_for_token(access_token)
    try:
        response = (
            client.table(TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        raise RuntimeError("Failed to read user model settings") from exc

    if response is None:
        return None

    return response.data


def upsert_user_model_settings(access_token: str, payload: dict) -> dict:
    client = get_supabase_for_token(access_token)
    try:
        response = client.table(TABLE_NAME).upsert(payload).execute()
    except Exception as exc:
        raise RuntimeError("Failed to save user model settings") from exc

    if response is None:
        return payload

    if response.data:
        return response.data[0]
    return payload
