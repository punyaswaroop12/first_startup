FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV REPO_ROOT=/app

WORKDIR /app/apps/api

COPY apps/api/pyproject.toml ./pyproject.toml
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/alembic ./alembic
COPY apps/api/app ./app
COPY seed-data /app/seed-data
COPY storage /app/storage

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["sh", "-c", "python -m app.db.seed && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]

