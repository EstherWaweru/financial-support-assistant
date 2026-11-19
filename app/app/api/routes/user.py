from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password


from app import schemas
from app.api import deps

from app import repositories

router = APIRouter()


@router.post("/register", response_model=schemas.UserRegisterResponse)
def create_user(
    request: schemas.UserRegisterRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    existing_user = repositories.user.get_by(db=db, email=request.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already in use. Register with another email",
        )

    hashed_password = hash_password(request.password)

    user_schema = schemas.UserCreate(
        email=request.email, hashed_password=hashed_password
    )
    user = repositories.user.create(db=db, obj_in=user_schema)

    return schemas.UserRegisterResponse(email=user.email, id=user.id)
