from app.models import UserModel, UserRole
from app.schemas.user import UserOutDto, UserInChangeRoleDto, ChangeUserActivityInDto

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException


async def change_role(
    dto: UserInChangeRoleDto, user: UserModel, session: AsyncSession
) -> UserOutDto:
    # Проверки у пользователя, который изменяет роль
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.role == UserRole.GUEST or user.role == UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="У пользователя недостаточно прав на изменеине данных",
        )

    query = select(UserModel).where(UserModel.id == dto.user_id)
    result = await session.execute(query)
    user_to_change = result.scalar_one_or_none()

    if not user_to_change:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь деактивирован")

    if user_to_change.id == user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя изменить свою собственную роль"
        )

    # Проверка иерархии для изменения роли
    if user.role == UserRole.MODERATOR:
        if dto.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=403, detail="Модератор не может назначать администраторов"
            )
        if user_to_change.role == UserRole.MODERATOR:
            raise HTTPException(
                status_code=403,
                detail="Модератор не может изменять роли других модераторов",
            )

    try:
        if user_to_change.role == dto.role:
            return UserOutDto.new(user_to_change)
        else:
            user_to_change.role = dto.role
            await session.commit()
            await session.refresh(user_to_change)
            return UserOutDto.new(user_to_change)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка при обновлении роли: {str(e)}"
        )


async def change_user_activity(
    dto: ChangeUserActivityInDto, user: UserModel, session: AsyncSession
) -> UserOutDto:
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.role == UserRole.GUEST or user.role == UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="У пользователя недостаточно прав на изменеине данных",
        )

    query = select(UserModel).where(UserModel.id == dto.user_id)
    result = await session.execute(query)
    user_to_change = result.scalar_one_or_none()

    if not user_to_change:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_to_change.id == user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя изменить свою собственную роль"
        )

    if user.role == UserRole.MODERATOR:
        if user_to_change.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Модератор не может деактивировать аккаунт админа",
            )
        if user_to_change.role == UserRole.MODERATOR:
            raise HTTPException(
                status_code=403,
                detail="Модератор не может деактивировать аккаунт другого модератора",
            )

    try:
        if user_to_change.is_active == dto.activity_flag:
            return UserOutDto.new(user_to_change)
        else:
            user_to_change.is_active = dto.activity_flag
            await session.commit()
            await session.refresh(user_to_change)
            return UserOutDto.new(user_to_change)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при изменения активности пользователя: {str(e)}",
        )
