import json
import random
import time
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt", 1883, 60)

def run_distance(client_id, factory_id, machine_id, loop=False):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/distance"
    
    while True:
        data = {
            "distance": random.randint(5, 30)
        }

        print(f"[Machine {machine_id}] DISTANCE: ", data)
        mqtt_client.publish(topic, json.dumps(data))
        
        if not loop:
            break
        time.sleep(1)