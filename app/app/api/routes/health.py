from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from app.api import deps

router = APIRouter()


@router.get("/status")
def check_readiness(db: Session = Depends(deps.get_db)) -> Any:
    """
    Endpoint for to check if the app is alive and healthy
    """

    try:
        db.execute(text("SELECT 1"))
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"{e._message()}")
    return {"status": "ok"}
