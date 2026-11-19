from datetime import datetime, timezone
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

from app.models import User, ConversationStatus

router = APIRouter()


@router.post("/create", response_model=schemas.ChatResponse)
def create_conversation(
    request: schemas.CreateConversationRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    customer_id = current_user.id
    conversation_schema = schemas.ConversationCreate(customer_id=customer_id)
    # Create conversation in db
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
        assistant_response = services.llm_chat(
            messages=messages, external_customer_id=current_user.external_customer_id
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
    # update conversation update
    conversation_schema = schemas.ConversationUpdate(
        updated_at=datetime.now(timezone.utc)
    )
    repositories.conversation.update(
        db=db, db_obj=conversation, obj_in=conversation_schema
    )
    return schemas.ChatResponse(
        response=assistant_response["response"], conversation_id=conversation.id
    )


@router.post("/{conversation_id}/message", response_model=schemas.ChatResponse)
def create_message(
    conversation_id: UUID,
    request: schemas.CreateMessageRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    customer_id = current_user.id
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

    if conversation.status == ConversationStatus.CLOSED.value:
        raise HTTPException(
            status_code=409,
            detail="This conversation is closed and cannot receive new messages.",
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
        response = services.llm_chat(
            messages=messages,
            external_customer_id=current_user.external_customer_id,
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
    # update conversation update
    conversation_schema = schemas.ConversationUpdate(
        updated_at=datetime.now(timezone.utc)
    )
    repositories.conversation.update(
        db=db, db_obj=conversation, obj_in=conversation_schema
    )
    # Return the response
    return schemas.ChatResponse(
        conversation_id=conversation_id,
        response=response["response"],
    )


@router.get(
    "/{conversation_id}",
    response_model=schemas.ConversationHistoryResponse,
)
def get_conversation_history(
    conversation_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    customer_id = current_user.id
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
    messages = repositories.message.get_multi(
        db=db,
        conversation_id=conversation_id,
    )

    # TODO: Move formatting tp formatter utils

    visible_messages = [
        schemas.MessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        for message in messages
        if message.role in {"User", "Assistant"} and message.content is not None
    ]
    return schemas.ConversationHistoryResponse(
        conversation=schemas.ConversationResponse(
            id=conversation.id,
            customer_id=conversation.customer_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        ),
        messages=visible_messages,
    )


@router.patch("/{conversation_id}/archive", response_model=schemas.ConversationResponse)
def archive_conversation(
    conversation_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    conversation = repositories.conversation.get_by(
        db=db,
        id=conversation_id,
        customer_id=current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )
    if conversation.status == ConversationStatus.CLOSED.value:
        return conversation
    update_schema = schemas.ConversationUpdate(status=ConversationStatus.CLOSED.value)
    conversation = repositories.conversation.update(
        db=db, db_obj=conversation, obj_in=update_schema
    )

    return conversation
