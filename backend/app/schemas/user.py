from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional
from datetime import datetime
from app.models.user import UserModel, UserRole


class UserOutDto(BaseModel):
    id: int
    nickname: str
    login: str
    role: str

    bio: Optional[str] = None
    last_login: Optional[datetime] = None
    email: Optional[str] = None

    is_active: bool
    is_email_verified: bool

    created_at: datetime
    updated_at: datetime

    @staticmethod
    def new(user: UserModel):
        return UserOutDto(
            id=user.id,
            nickname=user.nickname,
            login=user.login,
            role=user.role,
            bio=user.bio,
            last_login=user.last_login,
            email=user.email,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class UserInDto(BaseModel):
    nickname: Annotated[str, StringConstraints(min_length=2, max_length=30)]
    login: Annotated[str, StringConstraints(min_length=6, max_length=60)]
    password: Annotated[str, StringConstraints(min_length=4)]


class UserTokensDto(BaseModel):
    user_data: UserOutDto
    access_token: str
    refresh_token: str


class UserInChangeRoleDto(BaseModel):
    role: UserRole
    user_id: int
