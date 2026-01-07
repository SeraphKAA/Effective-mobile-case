from sqlalchemy import String, Boolean, DateTime, Text, Enum, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.database import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid
import enum

# Определяем Enum для ролей пользователя
class UserRole(str, enum.Enum):
    GUEST = "guest"
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    

class UserModel(BaseModel):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    
    # Уникальный логин для входа в систему
    login: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    # Хешированный пароль
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Публичное отображаемое имя (никнейм)
    nickname: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    # Email пользователя
    email: Mapped[Optional[str]] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=True
    )
    
    # Роль пользователя в системе
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role_enum"),
        default=UserRole.USER,
        nullable=False,
        index=True
    )
    
    # Дополнительная информация о пользователе
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None
    )
    
    # Статус пользователя 
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Подтвержден ли email
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Дата последнего входа
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )
    
    # Дата и время создания аккаунта
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Дата и время последнего обновления
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Методы для удобства
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
        return self.nickname or self.login
    