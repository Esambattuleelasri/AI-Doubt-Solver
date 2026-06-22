# ─────────────────────────────────────────────
#  auth/jwt_handler.py — JWT Token Utilities
# ─────────────────────────────────────────────
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def decode_user_id(token: str) -> Optional[int]:
    payload = verify_token(token)
    if payload:
        sub = payload.get("sub")
        try:
            return int(sub) if sub is not None else None
        except ValueError:
            return None
    return None
