from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Settings(BaseSettings):
    # Основные настройки
    PROJECT_NAME: str = "Effective Mobile case"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Simple backend for users"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # База данных PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    # JWT
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
    ]

    # URL приложения
    DOMAIN_URL: str = "http://localhost"
    REACT_APP_PUBLIC_URL: str = "http://localhost:8000"
    

    @property
    def DATABASE_URL(self) -> str:
        """
        Динамическое формирование URL для базы данных
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """
        URL для синхронных операций (например, Alembic)
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем экземпляр настроек
settings = Settings()
