FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY simulations/raw-data-generator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the simulation code
COPY simulations/raw-data-generator/ .

# Copy the shared models
COPY shared/ /app/shared/

# Set PYTHONPATH so it can find 'shared'
ENV PYTHONPATH=/app

CMD ["python", "main.py"]