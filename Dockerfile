FROM python:3.12-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
COPY README.md /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]