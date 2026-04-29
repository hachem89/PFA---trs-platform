import schedule
import time
import threading
from app.kpi_engine import calculate_kpis

def run_scheduler(app):
    """
    Runs the scheduling loop in a separate thread.
    """
    # Schedule the job every 1 minute for demonstration/prototype purposes.
    # In production, this might be every 5 minutes or hourly.
    schedule.every(1).minutes.do(lambda: run_job_with_context(app))

    def loop():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

def run_job_with_context(app):
    """
    Executes the KPI calculation within the Flask application context 
    so it can access the database.
    """
    with app.app_context():
        calculate_kpis()
