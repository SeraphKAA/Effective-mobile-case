from app.models import UserModel
from app.schemas.user import (
    UserInDto,
    UserOutDto,
    UserTokensDto,
)
from .authentication import (
    create_refresh_token,
    create_access_token,
    verify_token,
)

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
import re
from datetime import datetime, timezone


async def create_user(user_in_dto: UserInDto, session: AsyncSession) -> UserOutDto:
    # Валидация имени
    if not re.fullmatch(r"[A-Za-zА-Яа-яёЁ\s\-]+", user_in_dto.nickname):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Никнейм должно содержать только буквы, пробелы и дефисы.",
        )

    if len(user_in_dto.password) > 20:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пароль должен быть не длиннее 20 символов.",
        )

    query = select(exists().where(UserModel.login == user_in_dto.login))
    result = await session.execute(query)
    if result.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Логин уже существует. Пожалуйста, выберите другой.",
        )

    query = select(exists().where(UserModel.nickname == user_in_dto.nickname))
    result = await session.execute(query)
    if result.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Никнейм уже существует. Пожалуйста, выберите другой.",
        )

    user = UserModel(
        nickname=user_in_dto.nickname,
        login=user_in_dto.login,
        bio=None,
        last_login=None,
    )

    user.set_password(user_in_dto.password)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserOutDto.new(user)


async def delete_user(user_id: int, session: AsyncSession) -> None:
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await session.delete(user)
    await session.commit()


async def get_users(session: AsyncSession) -> list[UserOutDto]:
    query = select(UserModel)
    result = await session.execute(query)
    users = result.scalars().all()

    return [UserOutDto.new(user) for user in users]


async def login(
    response: Response, form_data: OAuth2PasswordRequestForm, session: AsyncSession
):
    query = select(UserModel).where(UserModel.login == form_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    elif not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Пользователь деактивирован. Обратитесь к администратору.",
        )

    try:
        user.last_login = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении last_login для пользователя {user.id}: {e}")

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response.set_cookie(
        key="user_id",
        value=f"{user.id}",
        httponly=False,
        secure=False,  # изменить если будет домен с защищенным протоколом https
        samesite="Lax",  # или None, посмотреть по ситуации
    )

    response.set_cookie(
        key="role",
        value=f"{user.role}",
        httponly=False,
        secure=False,  # изменить если будет домен с защищенным протоколом https
        samesite="Lax",  # или None, посмотреть по ситуации
    )

    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=False,
        secure=True,  # изменить если будет домен с защищенным протоколом https
        samesite="Lax",  # или None, посмотреть по ситуации
    )

    response.set_cookie(
        key="refresh_token",
        value=f"{refresh_token}",
        httponly=False,
        secure=True,  # изменить если будет домен с защищенным протоколом https
        samesite="Lax",  # или None, посмотреть по ситуации
    )

    return UserTokensDto(
        user_data=UserOutDto.new(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh(refresh_token: str, session: AsyncSession):
    payload = verify_token(refresh_token, "refresh")
    user_id: dict = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь деактивирован")

    return create_access_token(user)


async def get_user_by_id(user_id: int, session: AsyncSession) -> UserOutDto:
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserOutDto.new(user)