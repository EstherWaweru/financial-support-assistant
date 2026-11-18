from typing import Any
from uuid import UUID

from fastapi import Depends, APIRouter, HTTPException
from requests import Timeout, HTTPError
from sqlalchemy.orm import Session

from app import schemas
from app import repositories
from app.api import deps

from app import services
from app.utils.formatter import format_messages

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
        messages = [
            {
                "role": "user",
                "content": request.message,
            }
        ]
        assistant_response = services.generate_response(
            messages=messages, customer_id="customer_001"
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

    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        )
    #  Persist intermediate tool interactions

    for tool_message in assistant_response["tool_messages"]:
        message_schema = schemas.MessageCreate(
            role=tool_message["role"],
            content=tool_message.get("content"),
            conversation_id=conversation.id,
            tool_calls=tool_message.get("tool_calls"),
            tool_call_id=tool_message.get("tool_call_id"),
        )
        repositories.message.create(db=db, obj_in=message_schema)
    # Save the assistant's response
    message_schema = schemas.MessageCreate(
        role="Assistant",
        content=assistant_response["response"],
        conversation_id=conversation.id,
    )
    repositories.message.create(db=db, obj_in=message_schema)
    return schemas.ChatResponse(
        response=assistant_response["response"], conversation_id=conversation.id
    )


@router.post("/{conversation_id}/message", response_model=schemas.ChatResponse)
def create_message(
    conversation_id: UUID,
    request: schemas.CreateMessageRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    # TODO: Replace this with customer retried from auth
    customer_id = "customer_001"
    # Retrieve conversation and verify ownership
    conversation = repositories.conversation.get_by(
        db=db,
        id=conversation_id,
        customer_id=customer_id,
    )
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with id {conversation_id} for customer {customer_id} not found",
        )
    #  Retrieve existing conversation history
    previous_messages = repositories.message.get_multi(
        db=db,
        conversation_id=conversation_id,
    )

    # Convert database messages into LLM format
    messages = format_messages(previous_messages)

    # Save the new user message
    message_schema = schemas.MessageCreate(
        role="User", content=request.message, conversation_id=conversation.id
    )
    repositories.message.create(db=db, obj_in=message_schema)
    # Include the new message in the LLM context
    messages.append(
        {
            "role": "user",
            "content": request.message,
        }
    )
    try:
        response = services.generate_response(
            messages=messages,
            customer_id=customer_id,
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
    #  Persist intermediate tool interactions
    for tool_message in response["tool_messages"]:
        message_schema = schemas.MessageCreate(
            role=tool_message["role"],
            content=tool_message.get("content"),
            conversation_id=conversation.id,
            tool_calls=tool_message.get("tool_calls"),
            tool_call_id=tool_message.get("tool_call_id"),
        )
        repositories.message.create(db=db, obj_in=message_schema)
    # Persist the final assistant response
    message_schema = schemas.MessageCreate(
        role="Assistant", content=response["response"], conversation_id=conversation.id
    )
    repositories.message.create(db=db, obj_in=message_schema)
    # Return the response
    return schemas.ChatResponse(
        conversation_id=conversation_id,
        response=response["response"],
    )
