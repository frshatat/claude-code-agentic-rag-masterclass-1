from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.db.user_model_settings import get_user_model_settings, upsert_user_model_settings
from app.services.secret_crypto_service import encrypt_secret
from app.services.user_runtime_settings_service import get_user_runtime_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings")


class UserModelSettingsUpdate(BaseModel):
    llm_model_name: str = Field(min_length=1)
    llm_base_url: str = Field(min_length=1)
    llm_api_key: str | None = None
    embedding_model_name: str = Field(min_length=1)
    embedding_base_url: str = Field(min_length=1)
    embedding_api_key: str | None = None
    embedding_dimensions: int = Field(default=1536, gt=0)


@router.get("/model-config")
async def get_model_config(user: dict = Depends(get_current_user)):
    try:
        row = get_user_model_settings(user["access_token"], user["id"])
        resolved = get_user_runtime_settings(user["access_token"], user["id"], require_complete=False)
    except RuntimeError as exc:
        logger.exception("Failed to read encrypted settings")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "llm_model_name": resolved["llm_model_name"],
        "llm_base_url": resolved["llm_base_url"],
        "llm_api_key_set": bool((row or {}).get("llm_api_key_encrypted")),
        "embedding_model_name": resolved["embedding_model_name"],
        "embedding_base_url": resolved["embedding_base_url"],
        "embedding_api_key_set": bool((row or {}).get("embedding_api_key_encrypted")),
        "embedding_dimensions": resolved["embedding_dimensions"],
    }


@router.put("/model-config")
async def update_model_config(
    body: UserModelSettingsUpdate,
    user: dict = Depends(get_current_user),
):
    try:
        existing = get_user_model_settings(user["access_token"], user["id"]) or {}
    except RuntimeError as exc:
        logger.exception("Failed to read user settings before update")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    llm_api_key_encrypted = existing.get("llm_api_key_encrypted")
    embedding_api_key_encrypted = existing.get("embedding_api_key_encrypted")

    if body.llm_api_key and body.llm_api_key.strip():
        try:
            llm_api_key_encrypted = encrypt_secret(body.llm_api_key.strip())
        except RuntimeError as exc:
            logger.exception("Failed to encrypt LLM API key")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    if body.embedding_api_key and body.embedding_api_key.strip():
        try:
            embedding_api_key_encrypted = encrypt_secret(body.embedding_api_key.strip())
        except RuntimeError as exc:
            logger.exception("Failed to encrypt embedding API key")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    payload = {
        "user_id": user["id"],
        "llm_model_name": body.llm_model_name.strip(),
        "llm_base_url": body.llm_base_url.strip(),
        "llm_api_key_encrypted": llm_api_key_encrypted,
        "embedding_model_name": body.embedding_model_name.strip(),
        "embedding_base_url": body.embedding_base_url.strip(),
        "embedding_api_key_encrypted": embedding_api_key_encrypted,
        "embedding_dimensions": body.embedding_dimensions,
    }

    try:
        upsert_user_model_settings(user["access_token"], payload)
    except RuntimeError as exc:
        logger.exception("Settings encryption failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to save model settings")
        raise HTTPException(status_code=500, detail="Failed to save settings") from exc

    return {
        "status": "ok",
        "llm_api_key_set": bool(llm_api_key_encrypted),
        "embedding_api_key_set": bool(embedding_api_key_encrypted),
    }
