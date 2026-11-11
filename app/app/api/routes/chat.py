from typing import Any

from fastapi import APIRouter

from app import schemas, services

router = APIRouter()


@router.post("/create", response_model=schemas.ChatResponse)
def chat(
    chat_in: schemas.ChatRequest,
) -> Any:
    answer = services.generate_response(chat_in.message)
    return schemas.ChatResponse(response=answer)
