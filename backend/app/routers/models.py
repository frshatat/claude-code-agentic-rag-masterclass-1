from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.services.model_selection_service import (
    get_active_models_for_user,
    get_available_chat_models,
    get_available_embedding_models,
    set_active_models_for_user,
)

router = APIRouter(prefix="/models")


class ActiveModelsUpdate(BaseModel):
    chat_model: str | None = None
    embedding_model: str | None = None


@router.get("")
async def get_models(user: dict = Depends(get_current_user)):
    active = get_active_models_for_user(user["id"])
    return {
        "chat": {
            "current": active["chat_model"],
            "available": get_available_chat_models(),
        },
        "embedding": {
            "current": active["embedding_model"],
            "available": get_available_embedding_models(),
        },
    }


@router.put("/active")
async def update_active_models(
    body: ActiveModelsUpdate,
    user: dict = Depends(get_current_user),
):
    if body.chat_model is None and body.embedding_model is None:
        raise HTTPException(status_code=400, detail="No model update requested")

    try:
        active = set_active_models_for_user(
            user["id"],
            chat_model=body.chat_model,
            embedding_model=body.embedding_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "chat_model": active["chat_model"],
        "embedding_model": active["embedding_model"],
    }
