FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости и код
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Создаем директории для БД и миграций
RUN mkdir -p /app/sqlite_data && \
    mkdir -p /app/alembic/versions
