import json
import random
import time
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("mqtt", 1883, 60)

TOPIC = "client/client1/factory/f1/machine/m1/distance"


def run_distance(loop=False):
    while True:
        data = {
            "distance": random.randint(5, 30)
        }

        client.publish(TOPIC, json.dumps(data))
        print("DISTANCE:", data)

        if not loop:
            break

        time.sleep(1)