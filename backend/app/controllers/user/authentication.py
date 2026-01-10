from jose.exceptions import ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta, timezone
from typing import Literal, TypeAlias
from jose import jwt, JWTError
from os import environ
from sqlalchemy import select

from app.models.user import UserModel
from app.database.database import get_db
from app.config import settings


TokenType: TypeAlias = Literal["access"] | Literal["refresh"]

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(user: UserModel) -> str:
    """Создание access token"""
    data = {
        "user_id": user.id,
        "login": user.login,
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    # datetime в timestamp (секунды с эпохи)
    if isinstance(data["exp"], datetime):
        data["exp"] = int(data["exp"].timestamp())

    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_refresh_token(user: UserModel) -> str:
    """Создание refresh token"""
    data = {
        "user_id": user.id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    }

    # datetime в timestamp
    if isinstance(data["exp"], datetime):
        data["exp"] = int(data["exp"].timestamp())

    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def verify_token(token: str, token_type: TokenType):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET)
        if payload.get("type") != token_type:
            print(f"TYPE of PAYLOAD: {payload.get('type')}")
            raise HTTPException(status_code=403, detail="Неверный тип токена!")
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Истекло время жизни токена!")
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен невалиден!")


async def get_current_user(
    token: str = Depends(OAUTH2_SCHEME), db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user
