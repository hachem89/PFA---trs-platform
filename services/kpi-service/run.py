from app.main import app
from app.scheduler import start_kpi_scheduler
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    # Start background calculation thread
    print("🚀 Starting KPI Calculation Service...")
    start_kpi_scheduler(app)
    
    # Run the Flask API (port 5002)
    app.run(host="0.0.0.0", port=5002)
