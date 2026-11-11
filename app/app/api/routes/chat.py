from typing import Any

from fastapi import APIRouter, HTTPException
from requests import HTTPError, Timeout

from app import schemas, services

router = APIRouter()


@router.post("/create", response_model=schemas.ChatResponse)
def chat(
    chat_in: schemas.ChatRequest,
) -> Any:
    # TODO: Get the customer id by auth
    try:
        answer = services.generate_response(
            message=chat_in.message, customer_id="customer_001"
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
    return schemas.ChatResponse(response=answer)
