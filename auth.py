from datetime import datetime, timedelta
from jose import JWTError,jwt
from passlib.context import CryptContext
from fastapi import Depends ,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from typing import List
import os

SECRET_KEY = os.getenv("SECRET_KEY","changethisinproduction")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
bearer_scheme = HTTPBearer()

def get_current_user(creadentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = creadentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401,detail="invalid or expired token")
    return payload

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403,detail=f"Access denied. Required roles: {allowed_roles}")
        return current_user
    return role_checker


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str,hashed: str ) -> bool:
    return pwd_context.verify(plain,hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None