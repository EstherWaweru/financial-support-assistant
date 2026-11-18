from typing import Any

from fastapi import Depends, APIRouter, HTTPException
from requests import Timeout, HTTPError
from sqlalchemy.orm import Session

from app import schemas
from app import repositories
from app.api import deps

from app import services

router = APIRouter()


@router.post("/create", response_model=schemas.ChatResponse)
def create_conversation(
    request: schemas.CreateConversationRequest, db: Session = Depends(deps.get_db)
) -> Any:
    # TODO: Get the customer id by auth
    customer_id = "customer_001"
    conversation_schema = schemas.ConversationCreate(customer_id=customer_id)
    # 1. Create conversation in db
    conversation = repositories.conversation.create(
        db=db,
        obj_in=conversation_schema,
    )
    # create message in db
    message_schema = schemas.MessageCreate(
        role="User", content=request.message, conversation_id=conversation.id
    )
    repositories.message.create(db=db, obj_in=message_schema)
    try:

        # send message to llm
        assistant_response = services.generate_response(
            message=request.message, customer_id="customer_001"
        )

    except Timeout:
        raise HTTPException(
            status_code=504,
            detail="The service took too long to respond.",
        )

    except HTTPError:

        raise HTTPException(
            status_code=502,
            detail="Unable to communicate with the service.",
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        )

    # 4. Save the assistant's response
    message_schema = schemas.MessageCreate(
        role="Assistant", content=assistant_response, conversation_id=conversation.id
    )
    repositories.message.create(db=db, obj_in=message_schema)
    return schemas.ChatResponse(
        response=assistant_response, conversation_id=conversation.id
    )
