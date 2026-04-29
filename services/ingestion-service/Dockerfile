FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/ingestion-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ingestion service code
COPY services/ingestion-service /app

# Copy shared code
COPY shared /app/shared

EXPOSE 5000

CMD ["python", "run.py"]