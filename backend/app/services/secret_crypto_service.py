from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


def _cipher() -> Fernet:
    key = settings.secrets_encryption_key.strip()
    if not key:
        raise RuntimeError("SETTINGS_ENCRYPTION_KEY is required for secure API key storage")
    try:
        return Fernet(key.encode("utf-8"))
    except Exception as exc:
        raise RuntimeError("SETTINGS_ENCRYPTION_KEY is invalid") from exc


def encrypt_secret(value: str) -> str:
    cipher = _cipher()
    return cipher.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_secret(value: str | None) -> str | None:
    if not value:
        return None
    cipher = _cipher()
    try:
        return cipher.decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Failed to decrypt stored secret") from exc
