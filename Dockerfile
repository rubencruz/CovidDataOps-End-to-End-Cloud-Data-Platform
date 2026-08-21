FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY schemas/ ./schemas/

ENV PYTHONPATH=/app/src
ENV PORT=8080

CMD exec gunicorn \
    --bind :${PORT} \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    covid_pipeline.app:app