from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ThreadCreate(BaseModel):
    title: str | None = None


class ThreadResponse(BaseModel):
    id: UUID
    user_id: UUID
    openai_thread_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime
