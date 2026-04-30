import json
import random
import time
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client()
mqtt_client.connect("mqtt", 1883, 60)

def run_vibration(client_id, factory_id, machine_id, loop=False):
    topic = f"client/{client_id}/factory/{factory_id}/machine/{machine_id}/vibration"
    
    while True:
        data = {
            "vibration": round(random.uniform(0.5, 2.5), 2)
        }

        mqtt_client.publish(topic, json.dumps(data))
        
        if not loop:
            break
        time.sleep(2)