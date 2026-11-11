from typing import Any

from fastapi import APIRouter

from app import schemas, services

router = APIRouter()


@router.post("/create", response_model=schemas.ChatResponse)
def chat(
    chat_in: schemas.ChatRequest,
) -> Any:
    # TODO: Get the customer id by auth
    answer = services.generate_response(
        message=chat_in.message, customer_id="customer_001"
    )
    return schemas.ChatResponse(response=answer)
