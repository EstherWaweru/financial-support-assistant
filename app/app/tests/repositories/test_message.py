import uuid

from sqlalchemy.orm import Session

from app import repositories
from app.schemas import MessageCreate, ConversationCreate


def test_create_message(db: Session) -> None:
    customer_id = f"test_customer_{uuid.uuid4()}"
    conversation_in = ConversationCreate(customer_id=customer_id)

    conversation = repositories.conversation.create(
        db=db,
        obj_in=conversation_in,
    )
    role = "assistant"
    content = "Where is my transfer?"

    message_in = MessageCreate(
        role=role, content=content, conversation_id=conversation.id
    )

    message = repositories.message.create(
        db=db,
        obj_in=message_in,
    )
    assert message.role == role
    assert message.content == content
    assert message.conversation_id == conversation.id
