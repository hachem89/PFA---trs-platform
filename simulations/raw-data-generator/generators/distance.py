import time
import random
import json
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("127.0.0.1", 1883, 60)
client.loop_start() 

TOPIC = "client/client1/factory/f1/machine/m1/distance"

while True:
    data = {
        # "device_id": "raspi_abc123",
        "distance": random.randint(5, 30)
    }

    client.publish(TOPIC, json.dumps(data))
    print("Sent:", data)

    time.sleep(1)