from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    thread_id: UUID
    role: str
    content: str
    openai_message_id: str | None
    created_at: datetime
