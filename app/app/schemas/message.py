from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str
    conversation_id: UUID
    tool_calls: Optional[list[dict]] = None
    tool_call_id: Optional[str] = None
