import json
import random
import time
import paho.mqtt.client as mqtt

# Single persistent MQTT client for the whole thread/process
mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt", 1883, 60)

def run_camera(client_id, factory_id, machine_id, loop=False):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/camera"
    
    while True:
        data = {
            "class": random.choice(["good", "bad"]),
            "confidence": round(random.uniform(0.7, 1.0), 2)
        }
        print(f"[Machine {machine_id}] CAMERA: ", data)
        mqtt_client.publish(topic, json.dumps(data))
        
        if not loop:
            break
        time.sleep(3)