from __future__ import annotations

from cryptography.fernet import Fernet
import pytest

from app.services import secret_crypto_service


def test_encrypt_then_decrypt_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(secret_crypto_service.settings, "secrets_encryption_key", Fernet.generate_key().decode("utf-8"))

    encrypted = secret_crypto_service.encrypt_secret("super-secret")

    assert encrypted != "super-secret"
    assert secret_crypto_service.decrypt_secret(encrypted) == "super-secret"


def test_decrypt_secret_none_returns_none() -> None:
    assert secret_crypto_service.decrypt_secret(None) is None


def test_invalid_key_raises_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(secret_crypto_service.settings, "secrets_encryption_key", "not-a-valid-fernet-key")

    with pytest.raises(RuntimeError, match="SETTINGS_ENCRYPTION_KEY is invalid"):
        secret_crypto_service.encrypt_secret("x")
