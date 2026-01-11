from fastapi import APIRouter, Depends, Path, Header, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import (
    UserOutDto,
    UserInDto,
    UserInChangeRoleDto,
    ChangeUserActivityInDto,
)
from app.controllers import user as user_controller
from app.database.database import get_db


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOutDto)
async def create_user(user_in: UserInDto, session: AsyncSession = Depends(get_db)):
    """Создание пользователя"""
    return await user_controller.create_user(user_in, session)


@router.delete("/delete", status_code=204)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_db)):
    """Удаление пользователя по user_id"""
    await user_controller.delete_user(user_id, session)


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    """Создание токена и установка куки"""
    tokens = await user_controller.login(response, form_data, session)
    return {
        "token_type": "bearer",
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "user_data": tokens.user_data,
    }


@router.post("/refresh", response_model=str)
async def refresh(
    authorization: str = Header(...), session: AsyncSession = Depends(get_db)
):
    """Обновление Access-токена. В заголовке Authorization необходимо указать Refresh-токен"""
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Неверный формат токена")
    return await user_controller.refresh(token, session)


@router.get("", response_model=list[UserOutDto])
async def get_users(session: AsyncSession = Depends(get_db)):
    """Получение всех пользователей"""
    return await user_controller.get_users(session)


@router.get("/public/{user_id}", response_model=UserOutDto)
async def get_user_by_id(
    user_id: int = Path(..., gt=0), session: AsyncSession = Depends(get_db)
):
    """Возвращает публичную информацию о пользователе с данным user_id"""
    return await user_controller.get_user_by_id(user_id, session)


@router.get("/me", response_model=UserOutDto)
async def get_current_user_info(
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Возвращает подробную информацию о текущем аутентифицированном пользователе"""
    return await user_controller.get_user_by_id(user.id, session)


@router.patch("/change-role", response_model=UserOutDto)
async def change_user_role(
    dto: UserInChangeRoleDto,
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Изменение роли пользователя по user_id"""
    return await user_controller.change_role(dto, user, session)


@router.patch("/change-activity", response_model=UserOutDto)
async def change_user_activity(
    dto: ChangeUserActivityInDto,
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Изменение активности пользователя по user_id"""
    return await user_controller.change_user_activity(dto, user, session)


@router.patch("/email", response_model=UserOutDto)
async def set_email_for_user(
    email: str,
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Установка почты для текущего пользователя"""
    return await user_controller.set_email(email, user, session)


@router.patch("/email-active", response_model=UserOutDto)
async def verify_email_for_user(
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Заглушка установки состояния проверки почты для текущего пользователя"""
    # можно конечно было сделать через smtp протокол (соответственную библиотеку) но решил что это излишне для тестового задания
    return await user_controller.set_email_active(user, session)


@router.patch("/delete-email", response_model=UserOutDto)
async def delete_email_for_user(
    user=Depends(user_controller.authentication.get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Удаление почты для текущего пользователя"""
    return await user_controller.delete_email(user, session)


# эндпоинт на изменение полей bio, nickname, login. password