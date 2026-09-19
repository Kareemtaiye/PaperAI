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


def generate_access_token(user_id: str):
    return jwt.encode({"payload": user_id}, settings.secret_key, algorithm="HS256")


def verify_jwt(token: str):
    return jwt.decode(token, settings.secret_key, algorithm="HS256")
