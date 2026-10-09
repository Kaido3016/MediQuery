FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN useradd --create-home --uid 10001 appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations
RUN mkdir -p /data/uploads && chown -R appuser:appuser /app /data
USER appuser

ENV ENVIRONMENT=production UPLOAD_ROOT=/data/uploads
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
