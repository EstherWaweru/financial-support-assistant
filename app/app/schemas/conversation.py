from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.message import MessageResponse

from app.models import ConversationStatus


class ConversationCreate(BaseModel):
    customer_id: UUID


class ConversationResponse(BaseModel):
    id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime
    status: ConversationStatus


class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]


class CreateConversationRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ConversationUpdate(BaseModel):
    updated_at: datetime = datetime.now(timezone.utc)
    status: ConversationStatus = ConversationStatus.ACTIVE.value


class UpdateConversationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=2000)
