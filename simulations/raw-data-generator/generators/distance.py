import json
import random
import time

def run_distance(client_id, factory_id, machine_id, mqtt_client):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/distance"
    
    # Randomize between 3 and 9 to simulate realistic sensor noise
    data = {
        "distance": random.randint(3, 9)
    }

    print(f"[Machine {machine_id}] DISTANCE (Piece Trigger): ", data)
    mqtt_client.publish(topic, json.dumps(data))