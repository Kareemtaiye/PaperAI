from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import jwt
from app.core.config import settings

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

password_hash = PasswordHash.recommended()

DUMMY_HASH = PasswordHash.recommended().hash("dummy_hash")


def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(password: str, hash: str):
    return password_hash.verify(password, hash)


def generate_access_token(data: str):
    expiry_time = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {"sub": data, "exp": expiry_time}

    return jwt.encode({"sub": data}, settings.secret_key, algorithm="HS256")


def verify_jwt(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def generate_refresh_token():
    return secrets.token_hex(64)


def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def verify_websocket_token(token: str, user_id: str):
    """
    Validates JWT token for WebSocket connection.
    Returns True if valid and belongs to user_id.
    Returns False otherwise.
    """

    payload = verify_jwt(token)
    token_user_id = payload.get("sub")

    return token_user_id == user_id
