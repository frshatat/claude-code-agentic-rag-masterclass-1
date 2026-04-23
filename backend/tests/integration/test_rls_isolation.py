from __future__ import annotations

import json
import uuid
from urllib import error, request

import pytest

from app.config import settings
from app.db.supabase import get_supabase_admin, get_supabase_for_token


TIMEOUT_SECONDS = 20


def _request_json(url: str, method: str = "GET", headers: dict | None = None, body: dict | None = None):
    payload = None
    req_headers = headers.copy() if headers else {}
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")

    req = request.Request(url=url, method=method, headers=req_headers, data=payload)
    try:
        with request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data) if data else None
    except error.HTTPError as exc:
        data = exc.read().decode("utf-8")
        parsed = json.loads(data) if data else None
        return exc.code, parsed


def _create_user_with_admin(email: str, password: str) -> str:
    status, body = _request_json(
        f"{settings.supabase_url}/auth/v1/admin/users",
        method="POST",
        headers={
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        },
        body={
            "email": email,
            "password": password,
            "email_confirm": True,
        },
    )
    if status not in {200, 201} or not body or "id" not in body:
        raise RuntimeError(f"Failed to create user: status={status}, body={body}")
    return body["id"]


def _delete_user_with_admin(user_id: str) -> None:
    _request_json(
        f"{settings.supabase_url}/auth/v1/admin/users/{user_id}",
        method="DELETE",
        headers={
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        },
    )


def _sign_in(email: str, password: str) -> tuple[str, str]:
    status, body = _request_json(
        f"{settings.supabase_url}/auth/v1/token?grant_type=password",
        method="POST",
        headers={"apikey": settings.supabase_anon_key},
        body={"email": email, "password": password},
    )
    if status != 200 or not body or "access_token" not in body or "user" not in body:
        raise RuntimeError(f"Failed to sign in: status={status}, body={body}")
    return body["access_token"], body["user"]["id"]


@pytest.fixture(scope="module")
def two_users():
    suffix = uuid.uuid4().hex[:10]
    user_a_email = f"validation-a-{suffix}@example.com"
    user_b_email = f"validation-b-{suffix}@example.com"
    password = f"Passw0rd!{suffix}"

    user_a_id = _create_user_with_admin(user_a_email, password)
    user_b_id = _create_user_with_admin(user_b_email, password)

    token_a, signed_in_a_id = _sign_in(user_a_email, password)
    token_b, signed_in_b_id = _sign_in(user_b_email, password)

    assert user_a_id == signed_in_a_id
    assert user_b_id == signed_in_b_id

    resources: dict[str, list[str]] = {
        "threads": [],
        "documents": [],
    }

    try:
        yield {
            "user_a": {"id": user_a_id, "token": token_a},
            "user_b": {"id": user_b_id, "token": token_b},
            "resources": resources,
        }
    finally:
        admin = get_supabase_admin()
        for thread_id in resources["threads"]:
            try:
                admin.table("threads").delete().eq("id", thread_id).execute()
            except Exception:
                pass
        for document_id in resources["documents"]:
            try:
                admin.table("documents").delete().eq("id", document_id).execute()
            except Exception:
                pass

        _delete_user_with_admin(user_a_id)
        _delete_user_with_admin(user_b_id)


def test_threads_and_messages_are_isolated_by_rls(two_users) -> None:
    user_a = two_users["user_a"]
    user_b = two_users["user_b"]

    client_a = get_supabase_for_token(user_a["token"])
    client_b = get_supabase_for_token(user_b["token"])

    thread_id = str(uuid.uuid4())
    client_a.table("threads").insert(
        {
            "id": thread_id,
            "user_id": user_a["id"],
            "openai_thread_id": str(uuid.uuid4()),
            "title": "A private thread",
        }
    ).execute()
    two_users["resources"]["threads"].append(thread_id)

    client_a.table("messages").insert(
        {
            "thread_id": thread_id,
            "role": "user",
            "content": "private-message",
        }
    ).execute()

    thread_seen_by_b = client_b.table("threads").select("id").eq("id", thread_id).execute().data
    assert thread_seen_by_b == []

    messages_seen_by_b = client_b.table("messages").select("id").eq("thread_id", thread_id).execute().data
    assert messages_seen_by_b == []

    with pytest.raises(Exception):
        client_b.table("messages").insert(
            {
                "thread_id": thread_id,
                "role": "user",
                "content": "should-fail",
            }
        ).execute()


def test_documents_and_settings_are_isolated_by_rls(two_users) -> None:
    user_a = two_users["user_a"]
    user_b = two_users["user_b"]

    client_a = get_supabase_for_token(user_a["token"])
    client_b = get_supabase_for_token(user_b["token"])

    document_id = str(uuid.uuid4())
    client_a.table("documents").insert(
        {
            "id": document_id,
            "user_id": user_a["id"],
            "file_name": "private.txt",
            "file_size_bytes": 11,
            "content_hash": f"hash-{uuid.uuid4().hex}",
            "status": "complete",
        }
    ).execute()
    two_users["resources"]["documents"].append(document_id)

    settings_row = {
        "user_id": user_a["id"],
        "llm_model_name": "openai/gpt-4.1-mini",
        "llm_base_url": "https://example.invalid/v1",
        "embedding_model_name": "text-embedding-3-small",
        "embedding_base_url": "https://example.invalid/v1",
        "embedding_dimensions": 1536,
    }
    client_a.table("user_model_settings").upsert(settings_row).execute()

    docs_seen_by_b = client_b.table("documents").select("id").eq("id", document_id).execute().data
    assert docs_seen_by_b == []

    settings_seen_by_b = (
        client_b.table("user_model_settings").select("user_id").eq("user_id", user_a["id"]).execute().data
    )
    assert settings_seen_by_b == []
