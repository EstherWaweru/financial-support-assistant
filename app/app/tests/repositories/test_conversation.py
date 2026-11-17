import uuid

from sqlalchemy.orm import Session

from app import repositories


from app.schemas import ConversationCreate


def test_create_message(db: Session) -> None:
    customer_id = f"test_customer_{uuid.uuid4()}"

    conversation_in = ConversationCreate(customer_id=customer_id)

    conversation = repositories.conversation.create(
        db=db,
        obj_in=conversation_in,
    )
    assert conversation.customer_id == customer_id
