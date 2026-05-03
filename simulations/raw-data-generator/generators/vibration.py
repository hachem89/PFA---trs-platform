import json
import random
import time

def run_vibration(client_id, factory_id, machine_id, mqtt_client, is_running=True):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/vibration"
    
    if is_running:
        val = random.uniform(2.5, 4.5)
    else:
        val = random.uniform(0.1, 0.4)
        
    data = {
        "vibration": round(val, 2)
    }

    print(f"[Machine {machine_id}] VIBRATION: ", data)
    mqtt_client.publish(topic, json.dumps(data))