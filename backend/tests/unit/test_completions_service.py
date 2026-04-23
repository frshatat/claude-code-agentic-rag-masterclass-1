from __future__ import annotations

import asyncio

import pytest

from app.services import completions_service


class _FakeDelta:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.delta = _FakeDelta(content)


class _FakeChunk:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class _FakeStream:
    def __init__(self, tokens):
        self._tokens = tokens

    def __enter__(self):
        return iter(_FakeChunk(token) for token in self._tokens)

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeCompletions:
    def __init__(self, tokens):
        self.tokens = tokens
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeStream(self.tokens)


class _FakeChat:
    def __init__(self, tokens):
        self.completions = _FakeCompletions(tokens)


class _FakeClient:
    def __init__(self, tokens):
        self.chat = _FakeChat(tokens)


def test_build_messages_for_api_filters_invalid_entries() -> None:
    result = completions_service.build_messages_for_api(
        [
            {"role": "user", "content": "  hello "},
            {"role": "assistant", "content": "reply"},
            {"role": "not-valid", "content": "ignored"},
            {"role": "system", "content": "   "},
        ]
    )

    assert result == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "reply"},
    ]


def test_stream_chat_completion_yields_tokens(monkeypatch) -> None:
    fake_client = _FakeClient(["tok-a", "tok-b"])

    monkeypatch.setattr(
        completions_service,
        "get_user_runtime_settings",
        lambda _token, _uid: {
            "llm_api_key": "secret",
            "llm_base_url": "https://example.invalid/v1",
            "llm_model_name": "test-model",
        },
    )
    monkeypatch.setattr(completions_service, "get_openai_client", lambda **_kwargs: fake_client)

    async def _collect() -> list[str]:
        tokens = []
        async for token in completions_service.stream_chat_completion(
            message_history=[{"role": "user", "content": "hello"}],
            access_token="token",
            user_id="user-1",
            thread_id="thread-1",
        ):
            tokens.append(token)
        return tokens

    tokens = asyncio.run(_collect())

    assert tokens == ["tok-a", "tok-b"]
    assert fake_client.chat.completions.calls
    create_call = fake_client.chat.completions.calls[0]
    assert create_call["model"] == "test-model"
    assert create_call["user"] == "user-1"
    assert create_call["stream"] is True


def test_stream_chat_completion_raises_when_stream_creation_fails(monkeypatch) -> None:
    class _FailingCompletions:
        def create(self, **_kwargs):
            raise RuntimeError("boom")

    class _FailingClient:
        chat = type("_Chat", (), {"completions": _FailingCompletions()})

    monkeypatch.setattr(
        completions_service,
        "get_user_runtime_settings",
        lambda _token, _uid: {
            "llm_api_key": "secret",
            "llm_base_url": "https://example.invalid/v1",
            "llm_model_name": "test-model",
        },
    )
    monkeypatch.setattr(completions_service, "get_openai_client", lambda **_kwargs: _FailingClient())

    async def _collect() -> list[str]:
        tokens = []
        async for token in completions_service.stream_chat_completion(
            message_history=[{"role": "user", "content": "hello"}],
            access_token="token",
            user_id="user-1",
            thread_id="thread-1",
        ):
            tokens.append(token)
        return tokens

    with pytest.raises(RuntimeError, match="boom"):
        asyncio.run(_collect())
