from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from passlib.hash import bcrypt

from app.models.user import UserRole, UserModel
from .database import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def create_default_users(session: AsyncSession):
    try:
        # Список пользователей для создания
        default_users = [
            {
                "login": "Guest",
                "password": "guest",
                "nickname": "Гость",
                "email": "guest@example.com",
                "role": UserRole.GUEST,
                "is_active": True,
                "is_email_verified": False,
                "bio": "Гостевой аккаунт для демонстрации",
            },
            {
                "login": "User",
                "password": "User",
                "nickname": "ОбычныйПользователь",
                "email": "user@example.com",
                "role": UserRole.USER,
                "is_active": True,
                "is_email_verified": True,
                "bio": "Обычный пользователь системы",
            },
            {
                "login": "Moderator",
                "password": "moderator",
                "nickname": "Модератор",
                "email": "moderator@example.com",
                "role": UserRole.MODERATOR,
                "is_active": True,
                "is_email_verified": True,
                "bio": "Аккаунт модератора",
            },
            {
                "login": "Admin",
                "password": "admin",
                "nickname": "Администратор",
                "email": "admin@example.com",
                "role": UserRole.ADMIN,
                "is_active": True,
                "is_email_verified": True,
                "bio": "Аккаунт администратора",
            },
            {
                "login": "SuperAdmin",
                "password": "superadmin",
                "nickname": "СуперАдмин",
                "email": "superadmin@example.com",
                "role": UserRole.SUPER_ADMIN,
                "is_active": True,
                "is_email_verified": True,
                "bio": "Аккаунт супер администратора",
            },
        ]

        created_count = 0
        skipped_count = 0

        for user_data in default_users:
            # Проверяем, существует ли уже пользователь с таким логином
            existing_user = await session.execute(
                select(UserModel).where(UserModel.login == user_data["login"])
            )
            existing_user = existing_user.scalar_one_or_none()

            if existing_user:
                logger.info(
                    f"Пользователь {user_data['login']} уже существует, пропускаем"
                )
                skipped_count += 1
                continue

            # Создаем нового пользователя
            new_user = UserModel(
                login=user_data["login"],
                nickname=user_data["nickname"],
                email=user_data["email"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                is_email_verified=user_data["is_email_verified"],
                bio=user_data.get("bio"),
            )

            # Устанавливаем пароль
            new_user.hashed_password = bcrypt.hash(user_data["password"])

            # Добавляем в сессию
            session.add(new_user)
            created_count += 1

            logger.info(
                f"Создан пользователь: {user_data['login']} ({user_data['role'].value})"
            )

        # Коммитим изменения
        await session.commit()

        logger.info(
            f"Инициализация пользователей завершена. Создано: {created_count}, пропущено: {skipped_count}"
        )
        return {
            "created": created_count,
            "skipped": skipped_count,
            "total": len(default_users),
        }

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при создании предопределенных пользователей: {e}")
        raise


async def initialize_default_data():
    async with AsyncSessionLocal() as session:
        try:
            # Создаем пользователей
            users_result = await create_default_users(session)

            return {
                "success": True,
                "users": users_result,
                "message": "Инициализация данных завершена успешно",
            }

        except Exception as e:
            logger.error(f"Ошибка при инициализации данных: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка при инициализации данных",
            }
