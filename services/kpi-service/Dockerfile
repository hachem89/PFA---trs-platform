FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/kpi-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models and service code
COPY shared/ /app/shared/
COPY services/kpi-service/ /app/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
