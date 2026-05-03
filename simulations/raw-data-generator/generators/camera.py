import json
import random
import time

def run_camera(client_id, factory_id, machine_id, mqtt_client):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/camera"
    
    # Simulate high quality production: 95% good, 5% bad
    is_good = random.random() < 0.95
    
    data = {
        "class": "good" if is_good else "bad",
        "confidence": round(random.uniform(0.85, 0.99), 2)
    }
    
    print(f"[Machine {machine_id}] CAMERA (Inspection): ", data)
    mqtt_client.publish(topic, json.dumps(data))