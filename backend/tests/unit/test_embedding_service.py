from __future__ import annotations

import asyncio

from app.services import embedding_service


class _EmbeddingData:
    def __init__(self, embedding):
        self.embedding = embedding


class _EmbeddingResponse:
    def __init__(self, values):
        self.data = [_EmbeddingData(v) for v in values]


class _FakeEmbeddingsAPI:
    def __init__(self, values):
        self.values = values
        self.calls = []

    def create(self, *, model, input):
        self.calls.append({"model": model, "input": input})
        return _EmbeddingResponse(self.values)


class _FakeClient:
    def __init__(self, values):
        self.embeddings = _FakeEmbeddingsAPI(values)


def test_embed_texts_for_user_empty_input_returns_empty_list() -> None:
    result = asyncio.run(embedding_service.embed_texts_for_user("token", "user", []))
    assert result == []


def test_embed_texts_for_user_uses_runtime_settings(monkeypatch) -> None:
    fake_client = _FakeClient([[0.1, 0.2], [0.3, 0.4]])

    monkeypatch.setattr(
        embedding_service,
        "get_user_runtime_settings",
        lambda _token, _uid: {
            "embedding_model_name": "text-embedding-test",
            "embedding_api_key": "api-key",
            "embedding_base_url": "https://example.invalid/v1",
        },
    )
    monkeypatch.setattr(embedding_service, "get_embedding_client", lambda **_kwargs: fake_client)

    result = asyncio.run(embedding_service.embed_texts_for_user("token", "user", ["a", "b"]))

    assert result == [[0.1, 0.2], [0.3, 0.4]]
    assert fake_client.embeddings.calls == [{"model": "text-embedding-test", "input": ["a", "b"]}]
