FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости для PostgreSQL и других библиотек
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app ./app
COPY alembic.ini .

ENV PYTHONPATH=/app

# Создаем директорию для uploads
RUN mkdir -p /app/uploads/photoes

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Команда для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]