import os
import time

from generators.camera import run_camera
from generators.distance import run_distance
from generators.vibration import run_vibration


MODE = os.getenv("GENERATOR_MODE", "all")


def run_all():
    while True:
        run_distance()
        run_camera()
        run_vibration()
        time.sleep(1)


if MODE == "camera":
    run_camera(loop=True)

elif MODE == "distance":
    run_distance(loop=True)

elif MODE == "vibration":
    run_vibration(loop=True)

elif MODE == "all":
    run_all()

else:
    raise ValueError(f"Unknown GENERATOR_MODE: {MODE}")