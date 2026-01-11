from app.models import UserModel
from app.schemas.user import (
    UserOutDto,
)

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException
import re


async def set_email(email: str, user: UserModel, session: AsyncSession) -> UserOutDto:
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь деактивирован")

    # Хоть и предполагается что на фронте также производятся проверки почты и других полей
    # все равно решил дополнительно проверить
    if re.fullmatch(regex, email):
        user.email = email
        user.is_email_verified = False
        await session.commit()
        await session.refresh(user)
        return UserOutDto.new(user)

    else:
        raise HTTPException(status_code=400, detail="Неправильный формат почты")


async def set_email_active(user: UserModel, session: AsyncSession) -> UserOutDto:
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь деактивирован")

    if not user.email:
        raise HTTPException(
            status_code=400, detail="У пользователя не установлена почта"
        )

    if user.is_email_verified:
        return UserOutDto.new(user)

    else:
        user.is_email_verified = True
        await session.commit()
        await session.refresh(user)
        return UserOutDto.new(user)


async def delete_email(user: UserModel, session: AsyncSession) -> UserOutDto:
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь деактивирован")

    if not user.email:
        raise HTTPException(
            status_code=400, detail="У пользователя не установлена почта"
        )

    try:
        user.email = None
        user.is_email_verified = False
        await session.commit()
        await session.refresh(user)
        return UserOutDto.new(user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка при удалении почты: {str(e)}"
        )
