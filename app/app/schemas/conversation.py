from pydantic import BaseModel


class ConversationCreate(BaseModel):
    customer_id: str
