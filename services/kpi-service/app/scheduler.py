import time
import threading
import logging
from datetime import datetime, timedelta, timezone
from app.db import db
from shared.models.machine import Machine
from shared.models.kpi_snapshot import KpiSnapshot
from app.queries import get_window_events, get_last_state_before
from app.kpi_engine import calculate_window_kpis

logger = logging.getLogger(__name__)

def align_to_window(interval_minutes=5):
    """Wait until the next 5-minute boundary."""
    now = datetime.now(timezone.utc)
    seconds_to_wait = (interval_minutes * 60) - (now.minute % interval_minutes * 60 + now.second)
    
    # If we are exactly on the boundary, wait for the full interval
    if seconds_to_wait == 0:
        seconds_to_wait = interval_minutes * 60
        
    logger.info(f"Alignment: Waiting {seconds_to_wait}s for the next boundary...")
    time.sleep(seconds_to_wait)

def run_scheduler(app):
    """Background loop that executes every 5 minutes."""
    with app.app_context():
        while True:
            align_to_window(5)
            
            # Define window boundaries
            end_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            start_time = end_time - timedelta(minutes=5)
            
            logger.info(f"--- Starting KPI Batch for window {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} ---")
            
            try:
                machines = db.session.query(Machine).all()
                for machine in machines:
                    try:
                        # 1. Get Events and Context
                        events = get_window_events(db_session=db.session, machine_id=machine.id, start_time=start_time, end_time=end_time)
                        initial_state = get_last_state_before(db_session=db.session, machine_id=machine.id, start_time=start_time)
                        
                        # 2. Calculate
                        kpis = calculate_window_kpis(machine, events, initial_state, start_time, end_time)
                        
                        # 3. Save Snapshot
                        snapshot = KpiSnapshot(
                            client_id=machine.factory.client_id,
                            factory_id=machine.factory_id,
                            machine_id=machine.id,
                            trs=kpis['trs'],
                            tdo=kpis['tdo'],
                            tp=kpis['tp'],
                            tq=kpis['tq'],
                            total_pieces=kpis['total_pieces'],
                            good_pieces=kpis['good_pieces'],
                            defective_pieces=kpis['defective_pieces'],
                            runtime_seconds=kpis['runtime_seconds'],
                            recorded_at=end_time
                        )
                        db.session.add(snapshot)
                        db.session.commit() # Commit per machine for resilience
                        
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error processing machine {machine.id}: {e}")
                
                logger.info(f"--- KPI Batch Completed ---")
                
            except Exception as e:
                logger.error(f"General Scheduler Error: {e}")

def start_kpi_scheduler(app):
    thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
    thread.start()
    return thread
