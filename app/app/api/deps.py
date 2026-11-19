from collections.abc import Generator

from typing import Annotated
from uuid import UUID

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

from app import repositories
from app.core.security import decode_access_token
from app.models import User

bearer_scheme = HTTPBearer()


def get_db() -> Generator:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id: UUID = decode_access_token(token.credentials)
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise credentials_exception

    user = repositories.user.get(db=db, id=user_id)

    if user is None:
        raise credentials_exception

    return user
