from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from app.config import settings
from app.views import api_router
from app.database.database import engine, BaseModel, check_db_connection
from app.database.init_data import initialize_default_data

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске приложения
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")

    # Проверка подключения к бд
    db_connected = await check_db_connection()
    if not db_connected:
        logger.error(
            "Failed to connect to database. Application may not work properly."
        )

    logger.info("Application startup completed successfully")

    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    logger.info("Initializing default data...")
    init_result = await initialize_default_data()
    if init_result["success"]:
        logger.info(f"Default data initialized successfully: {init_result}")
    else:
        logger.warning(f"Default data initialization failed: {init_result}")

    logger.info("Application startup completed successfully")

    yield

    # При остановке приложения
    logger.info("Shutting down application...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение роутеров
app.include_router(api_router)


# Health check endpoint с проверкой БД
@app.get("/health")
async def health_check():
    """
    Проверка здоровья приложения
    """
    db_status = "connected" if await check_db_connection() else "disconnected"

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "api_docs": f"{settings.DOMAIN_URL}:{settings.PORT}/api/docs",
    }


@app.get("/")
async def root():
    """
    Корневой endpoint
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": (
            f"{settings.DOMAIN_URL}:{settings.PORT}/api/docs"
            if settings.DEBUG
            else None
        ),
        "health_check": f"{settings.DOMAIN_URL}:{settings.PORT}/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
