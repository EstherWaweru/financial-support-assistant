from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    role: str
    content: Optional[str] = None
    conversation_id: UUID
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: Optional[str] = None
    created_at: datetime


class CreateMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class MessageUpdate(BaseModel):
    pass
