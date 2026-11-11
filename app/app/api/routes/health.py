from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def check_readiness() -> Any:
    """
    Endpoint for to check if the app is alive
    """
    return {"status": "ok"}
