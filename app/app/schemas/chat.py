from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="Customer's message",
    )
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: UUID
