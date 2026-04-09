import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.db import threads as db
from app.models.message import MessageCreate
from app.models.thread import ThreadCreate, ThreadResponse
from app.services import openai_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    body: ThreadCreate,
    user: dict = Depends(get_current_user),
):
    openai_thread_id = await openai_service.create_openai_thread()
    thread = db.create_thread(
        user_id=user["id"],
        access_token=user["access_token"],
        openai_thread_id=openai_thread_id,
        title=body.title,
    )
    return thread


@router.get("/threads")
async def list_threads(user: dict = Depends(get_current_user)):
    return db.get_threads(user["id"], user["access_token"])


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str, user: dict = Depends(get_current_user)):
    thread = db.get_thread(thread_id, user["id"], user["access_token"])
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.delete("/threads/{thread_id}", status_code=204)
async def delete_thread(thread_id: str, user: dict = Depends(get_current_user)):
    thread = db.get_thread(thread_id, user["id"], user["access_token"])
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    db.delete_thread(thread_id, user["id"], user["access_token"])


@router.post("/threads/{thread_id}/messages")
async def send_message(
    thread_id: str,
    body: MessageCreate,
    user: dict = Depends(get_current_user),
):
    thread = db.get_thread(thread_id, user["id"], user["access_token"])
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    db.add_message(
        access_token=user["access_token"],
        thread_id=thread_id,
        role="user",
        content=body.content,
    )

    message_history = sorted(
        [*(thread.get("messages") or []), {"role": "user", "content": body.content}],
        key=lambda message: message.get("created_at", ""),
    )

    async def event_stream():
        full_response = []
        try:
            async for token in openai_service.stream_assistant_response(
                message_history=message_history,
                user_message=body.content,
                user_id=user["id"],
                thread_id=thread_id,
            ):
                full_response.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"

            assistant_content = "".join(full_response)
            db.add_message(
                access_token=user["access_token"],
                thread_id=thread_id,
                role="assistant",
                content=assistant_content,
            )
        except Exception:
            logger.exception("Failed while streaming assistant response")
            yield f"data: {json.dumps({'error': 'Assistant stream failed'})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
