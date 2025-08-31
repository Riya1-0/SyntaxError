# import time
# import random
# import requests
# from datetime import datetime

# API_URL = "http://127.0.0.1:8000/ingest"

# while True:
#     data = {
#         "temperature": round(random.uniform(-20, 60), 2),   # °C
#         "pressure": round(random.uniform(10, 200), 2),      # bar
#         "storage": round(random.uniform(100, 1000), 2),     # kg H2
#         "timestamp": datetime.now().isoformat()
#     }
#     try:
#         r = requests.post(API_URL, json=data)
#         print("Sent:", data, "Response:", r.json())
#     except Exception as e:
#         print("Error:", e)
#     time.sleep(2)  # send every 2s


# simulator/simulator.py
import time, random, requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000/ingest"

while True:
    # normal reading
    pressure = round(random.uniform(10, 120), 2)
    # occasionally force a spike so you can see alerts in UI
    if random.random() < 0.12:  # ~12% chance per send
        pressure = round(random.uniform(151, 230), 2)

    data = {
        "temperature": round(random.uniform(-20, 60), 2),
        "pressure": pressure,
        "storage": round(random.uniform(100, 1000), 2),
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        r = requests.post(API_URL, json=data, timeout=5)
        print("Sent:", data, "=>", r.json())
    except Exception as e:
        print("Error:", e)
    time.sleep(2)
