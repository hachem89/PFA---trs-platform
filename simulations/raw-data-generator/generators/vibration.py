import json
import random
import time
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("mqtt", 1883, 60)

TOPIC = "client/550e8400-e29b-41d4-a716-446655440000/factory/550e8400-e29b-41d4-a716-446655440001/machine/550e8400-e29b-41d4-a716-446655440002/vibration"


def run_vibration(loop=False):
    while True:
        data = {
            "vibration": round(random.uniform(0.5, 2.5), 2)
        }

        client.publish(TOPIC, json.dumps(data))
        print("VIBRATION:", data)

        if not loop:
            break

        time.sleep(2)