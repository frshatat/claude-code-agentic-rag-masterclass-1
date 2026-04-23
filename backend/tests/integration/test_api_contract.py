from __future__ import annotations

import json
import os
from urllib import error, parse, request

import pytest

from app.config import settings


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


def _sign_in(email: str, password: str) -> str:
    url = f"{settings.supabase_url}/auth/v1/token?grant_type=password"
    status, body = _request_json(
        url,
        method="POST",
        headers={"apikey": settings.supabase_anon_key},
        body={"email": email, "password": password},
    )
    if status != 200 or not body or not body.get("access_token"):
        raise RuntimeError(f"Failed to sign in test user: status={status}, body={body}")
    return body["access_token"]


@pytest.fixture(scope="session")
def user_token(test_credentials: tuple[str, str]) -> str:
    email, password = test_credentials
    return _sign_in(email, password)


@pytest.fixture(scope="session", autouse=True)
def require_backend_up(backend_base_url: str) -> None:
    status, body = _request_json(f"{backend_base_url}/health")
    if status != 200 or body != {"status": "ok"}:
        pytest.skip("Backend is not running on BACKEND_BASE_URL; skipping API integration tests")


def test_protected_threads_requires_auth(backend_base_url: str) -> None:
    status, body = _request_json(f"{backend_base_url}/api/threads")
    assert status == 403
    assert body is not None


def test_authenticated_threads_list_returns_200(backend_base_url: str, user_token: str) -> None:
    status, body = _request_json(
        f"{backend_base_url}/api/threads",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert status == 200
    assert isinstance(body, list)


def test_model_settings_round_trip(backend_base_url: str, user_token: str) -> None:
    get_status, before = _request_json(
        f"{backend_base_url}/api/settings/model-config",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_status == 200
    assert isinstance(before, dict)

    update_payload = {
        "llm_model_name": "openai/gpt-4.1-mini",
        "llm_base_url": before["llm_base_url"],
        "llm_api_key": "",
        "embedding_model_name": "text-embedding-3-small",
        "embedding_base_url": before["embedding_base_url"],
        "embedding_api_key": "",
        "embedding_dimensions": 1536,
    }

    put_status, put_body = _request_json(
        f"{backend_base_url}/api/settings/model-config",
        method="PUT",
        headers={"Authorization": f"Bearer {user_token}"},
        body=update_payload,
    )
    assert put_status == 200
    assert put_body == {
        "status": "ok",
        "llm_api_key_set": before["llm_api_key_set"],
        "embedding_api_key_set": before["embedding_api_key_set"],
    }

    after_status, after = _request_json(
        f"{backend_base_url}/api/settings/model-config",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert after_status == 200
    assert after["llm_model_name"] == "openai/gpt-4.1-mini"
    assert after["embedding_model_name"] == "text-embedding-3-small"
    assert after["embedding_dimensions"] == 1536
