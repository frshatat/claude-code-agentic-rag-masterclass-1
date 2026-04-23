from __future__ import annotations

from app.services import user_runtime_settings_service


def test_runtime_settings_incomplete_raises_by_default(monkeypatch) -> None:
    monkeypatch.setattr(user_runtime_settings_service, "get_user_model_settings", lambda _token, _uid: None)
    monkeypatch.setattr(user_runtime_settings_service, "decrypt_secret", lambda _value: None)

    try:
        user_runtime_settings_service.get_user_runtime_settings("token", "user-1")
        assert False, "Expected RuntimeError for incomplete model settings"
    except RuntimeError as exc:
        assert str(exc) == "User model settings are incomplete. Please configure model settings."


def test_runtime_settings_can_return_partial_when_require_complete_false(monkeypatch) -> None:
    monkeypatch.setattr(user_runtime_settings_service, "get_user_model_settings", lambda _token, _uid: None)
    monkeypatch.setattr(user_runtime_settings_service, "decrypt_secret", lambda _value: None)

    resolved = user_runtime_settings_service.get_user_runtime_settings("token", "user-1", require_complete=False)

    assert resolved["llm_model_name"] == ""
    assert resolved["llm_base_url"] == ""
    assert resolved["llm_api_key"] is None
    assert resolved["embedding_model_name"] == ""
    assert resolved["embedding_base_url"] == ""
    assert resolved["embedding_api_key"] is None
    assert resolved["embedding_dimensions"] == 1536


def test_runtime_settings_prefer_user_values_and_decrypted_secrets(monkeypatch) -> None:
    row = {
        "llm_model_name": "user-llm",
        "llm_base_url": "https://user-llm.example/v1",
        "llm_api_key_encrypted": "enc-llm",
        "embedding_model_name": "user-embed",
        "embedding_base_url": "https://user-embed.example/v1",
        "embedding_api_key_encrypted": "enc-embed",
        "embedding_dimensions": 3072,
    }

    monkeypatch.setattr(user_runtime_settings_service, "get_user_model_settings", lambda _token, _uid: row)
    monkeypatch.setattr(
        user_runtime_settings_service,
        "decrypt_secret",
        lambda value: {"enc-llm": "user-llm-key", "enc-embed": "user-embed-key"}.get(value),
    )

    resolved = user_runtime_settings_service.get_user_runtime_settings("token", "user-1")

    assert resolved["llm_model_name"] == "user-llm"
    assert resolved["llm_base_url"] == "https://user-llm.example/v1"
    assert resolved["llm_api_key"] == "user-llm-key"
    assert resolved["embedding_model_name"] == "user-embed"
    assert resolved["embedding_base_url"] == "https://user-embed.example/v1"
    assert resolved["embedding_api_key"] == "user-embed-key"
    assert resolved["embedding_dimensions"] == 3072
