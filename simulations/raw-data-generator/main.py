import os
import time
import random
import threading
import json
import paho.mqtt.client as mqtt
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

def simulate_machine(client_id, factory_id, machine_id, tc, stop_event):
    """Runs a coordinated simulation loop adjusted to the machine's theoretical speed."""
    print(f"DEBUG: Starting dynamic simulation for Machine {machine_id} (Tc={tc}s)")
    
    local_client = mqtt.Client()
    try:
        local_client.connect("mqtt", 1883, 60)
        local_client.loop_start()
    except Exception as e:
        print(f"CRITICAL: Machine {machine_id} could not connect to MQTT: {e}")
        return

    while not stop_event.is_set():
        try:
            # 1. State Decision (95% chance of running)
            is_running = random.random() < 0.95
            
            if is_running:
                # A. Send 'High' Vibration
                run_vibration(client_id, factory_id, machine_id, local_client, is_running=True)
                
                # B. RESET Distance Sensor
                local_client.publish(f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/distance", 
                                     json.dumps({"distance": 30}))
                time.sleep(0.3)
                
                # C. TRIGGER Piece Detection
                run_distance(client_id, factory_id, machine_id, local_client)
                time.sleep(0.3)
                
                # D. Send Inspection
                run_camera(client_id, factory_id, machine_id, local_client)
                
                # E. WAIT based on Theoretical Cycle Time (Tc)
                # To get ~90% Performance, we produce at a rate slightly slower than Tc
                # Total overhead so far is 0.6s
                target_cycle = tc * random.uniform(1.05, 1.15)
                wait_time = max(0.1, target_cycle - 0.6)
                time.sleep(wait_time)
            else:
                # Machine is 'Stopped'
                run_vibration(client_id, factory_id, machine_id, local_client, is_running=False)
                time.sleep(tc or 2.0) # Wait a bit before checking state again
                
        except Exception as e:
            print(f"ERROR in Machine {machine_id} thread: {e}")
    
    local_client.loop_stop()
    local_client.disconnect()

def main():
    print("LOG: Starting Discovery Loop for Simulation...")
    active_simulations = {}
    
    while True:
        try:
            db = SessionLocal()
            machines_with_clients = db.query(Machine, Factory.client_id).join(Factory).all()
            db.close()
            
            current_machine_ids = {str(m[0].id) for m in machines_with_clients}
            
            # 1. STOP deleted machines
            for machine_id in list(active_simulations.keys()):
                if machine_id not in current_machine_ids:
                    active_simulations[machine_id].set()
                    del active_simulations[machine_id]
            
            # 2. START/UPDATE machines
            for machine, client_id in machines_with_clients:
                m_id = str(machine.id)
                tc = machine.theoretical_cycle_time or 2.0 # Default to 2s if not set
                
                if m_id not in active_simulations:
                    print(f"LOG: Starting simulation for Machine {m_id} (Tc={tc}s)")
                    stop_event = threading.Event()
                    thread = threading.Thread(
                        target=simulate_machine, 
                        args=(str(client_id), str(machine.factory_id), m_id, tc, stop_event),
                        daemon=True
                    )
                    thread.start()
                    active_simulations[m_id] = stop_event
            
        except Exception as e:
            print(f"ERROR in discovery loop: {e}")
            
        time.sleep(20)

if __name__ == "__main__":
    main()