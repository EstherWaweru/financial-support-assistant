from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app import repositories
from app.core.security import verify_password, create_access_token

from app.api import deps

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
def login_user(
    request: schemas.UserLoginRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    user = repositories.user.get_by(
        db=db,
        email=request.email,
    )

    if user is None or not verify_password(
        request.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )
