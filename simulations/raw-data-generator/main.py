import os
import time
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import shared models
from shared.models.machine import Machine
from shared.models.factory import Factory

# Import generators
from generators.camera import run_camera
from generators.distance import run_distance
from generators.vibration import run_vibration

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def simulate_machine(client_id, factory_id, machine_id, stop_event):
    """Runs a dedicated simulation loop for a single machine."""
    print(f"DEBUG: Starting simulation thread for Machine {machine_id}")
    while not stop_event.is_set():
        try:
            # We call each generator once per loop (non-blocking)
            run_distance(client_id, factory_id, machine_id)
            run_camera(client_id, factory_id, machine_id)
            run_vibration(client_id, factory_id, machine_id)
        except Exception as e:
            print(f"ERROR in Machine {machine_id} thread: {e}")
            
        time.sleep(3) # Frequency of the simulation for this machine
    
    print(f"DEBUG: Stopping simulation thread for Machine {machine_id} (Machine deleted)")

def main():
    print("LOG: Starting Discovery Loop for Simulation...")
    # Dictionary to track active threads: {machine_id: stop_event}
    active_simulations = {}
    
    while True:
        try:
            db = SessionLocal()
            # Fetch all machines currently in the database
            machines_with_clients = db.query(Machine, Factory.client_id).join(Factory).all()
            db.close()
            
            current_machine_ids = {str(m[0].id) for m in machines_with_clients}
            
            # 1. STOP simulations for machines that were deleted
            for machine_id in list(active_simulations.keys()):
                if machine_id not in current_machine_ids:
                    print(f"LOG: Machine {machine_id} no longer in DB. Stopping simulation...")
                    active_simulations[machine_id].set() # Signal thread to stop
                    del active_simulations[machine_id]
            
            # 2. START simulations for new machines
            for machine, client_id in machines_with_clients:
                m_id = str(machine.id)
                if m_id not in active_simulations:
                    stop_event = threading.Event()
                    thread = threading.Thread(
                        target=simulate_machine, 
                        args=(str(client_id), str(machine.factory_id), m_id, stop_event),
                        daemon=True
                    )
                    thread.start()
                    active_simulations[m_id] = stop_event
                    print(f"LOG: New machine detected. ID: {m_id}")
            
        except Exception as e:
            print(f"ERROR in discovery loop: {e}")
            
        time.sleep(20) # Check for DB changes every 20 seconds

if __name__ == "__main__":
    main()