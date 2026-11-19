from datetime import datetime, timezone, timedelta
from uuid import UUID

import jwt

from pwdlib import PasswordHash
from app.core.config import get_settings

settings = get_settings()

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: UUID) -> str:
    """Create a signed JWT access token."""

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    """Validate a JWT and return the authenticated user's UUID."""

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    return UUID(payload["sub"])
