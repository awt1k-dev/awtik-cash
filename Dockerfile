# Используем легковесный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения, чтобы Python не создавал .pyc файлы и сразу выводил логи
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (нужны для сборки psycopg2 для PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное содержимое проекта
# (main.py, папку app со статикой и шаблонами)
COPY . .

# Открываем порт, который указали в docker-compose
EXPOSE 8000

# Команда запуска совпадает с той, что в docker-compose
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]