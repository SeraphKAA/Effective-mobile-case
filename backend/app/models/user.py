from sqlalchemy import String, Boolean, DateTime, Text, Enum, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.database.database import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid
import enum
from passlib.hash import bcrypt


class UserRole(str, enum.Enum):
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserModel(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    login: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    nickname: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )

    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role_enum"),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )

    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, login='{self.login}', nickname='{self.nickname}')>"

    @property
    def is_admin(self) -> bool:
        """Проверка, является ли пользователь администратором"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def is_moderator(self) -> bool:
        """Проверка, является ли пользователь модератором"""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    @property
    def display_name(self) -> str:
        """Отображаемое имя пользователя"""
        return self.nickname

    def set_password(self, password: str):
        """Установить хешированный пароль"""
        self.hashed_password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        """Проверка пароля"""
        try:
            result = bcrypt.verify(password, self.hashed_password)
            return result
        except Exception as e:
            return False
