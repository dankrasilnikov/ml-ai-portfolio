FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml poetry.lock* requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . .
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "apps.agentic.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
