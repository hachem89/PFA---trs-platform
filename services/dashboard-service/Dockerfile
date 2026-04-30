FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 (if needed, though binary is usually enough)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY services/dashboard-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY services/dashboard-service/ /app/

# Copy the shared library
COPY shared/ /app/shared/

# Expose the dashboard port
EXPOSE 5001

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "run:app"]
