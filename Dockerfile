FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false

# Устанавливаем poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Кэш слоёв: сначала только зависимости
COPY pyproject.toml poetry.lock /app/
RUN poetry install --only main --no-interaction --no-ansi

# Копируем остальной код
COPY . /app

# Непривилегированный пользователь
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# UVicorn (можно потом переключиться на gunicorn+uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]