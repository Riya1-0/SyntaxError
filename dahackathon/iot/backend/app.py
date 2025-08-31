# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import List
# import datetime
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # for testing allow all
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )




# # Store sensor data in memory (for demo)
# sensor_data = []

# class SensorReading(BaseModel):
#     temperature: float
#     pressure: float
#     storage: float
#     timestamp: str

# @app.post("/ingest")
# def ingest_data(reading: SensorReading):
#     """Receive fake IoT data and store it"""
#     sensor_data.append(reading.dict())
#     # Keep only last 100 readings
#     if len(sensor_data) > 100:
#         sensor_data.pop(0)
#     return {"status": "success", "received": reading.dict()}

# @app.get("/latest")
# def get_latest():
#     """Get latest sensor reading"""
#     if sensor_data:
#         return sensor_data[-1]
#     return {"error": "No data yet"}

# @app.get("/history")
# def get_history():
#     """Get last 100 readings"""
#     return sensor_data


# backend/app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import asyncio
import random

app = FastAPI(title="Hydrogen IoT Backend with Alerts")

# CORS - allow your frontend origin (for dev allow all)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:5173"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws/iot")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Fake IoT readings
        data = {
            "temperature": round(random.uniform(20, 100), 2),
            "pressure": round(random.uniform(80, 200), 2),
            "storage": round(random.uniform(30, 100), 2)
        }

        # Add alert condition
        if data["pressure"] > 150:
            data["alert"] = "⚠️ High Pressure! Above 150 bar."
        else:
            data["alert"] = None

        await websocket.send_json(data)
        await asyncio.sleep(2)  # send every 2 sec

# In-memory stores (demo). Replace with DB in production.
sensor_data: List[dict] = []
alerts: List[dict] = []

THRESHOLD_PRESSURE = 150.0  # alert threshold

class SensorReading(BaseModel):
    temperature: float
    pressure: float
    storage: float
    timestamp: str

# Simple WebSocket connection manager to broadcast messages to all clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                # if sending fails, remove connection
                self.disconnect(connection)

manager = ConnectionManager()

@app.post("/ingest")
async def ingest_data(reading: SensorReading):
    """Receive a sensor reading, check for alerts, store and broadcast."""
    data = reading.dict()
    # store reading
    sensor_data.append(data)
    if len(sensor_data) > 2000:
        sensor_data.pop(0)

    # always broadcast new reading (so frontend can get real-time updates)
    asyncio.create_task(manager.broadcast_json({"event": "reading", "reading": data}))

    # check for pressure alert
    if data["pressure"] > THRESHOLD_PRESSURE:
        alert = {
            "id": datetime.utcnow().isoformat(),
            "type": "pressure",
            "message": f"High pressure detected: {data['pressure']} bar",
            "value": data["pressure"],
            "timestamp": data["timestamp"],
            "active": True
        }
        alerts.insert(0, alert)  # newest first
        # keep last 200 alerts
        if len(alerts) > 200:
            alerts.pop()

        # broadcast alert immediately (non-blocking)
        asyncio.create_task(manager.broadcast_json({"event": "alert", "alert": alert}))

    return {"status": "success", "received": data}

@app.get("/latest")
def get_latest():
    if sensor_data:
        return sensor_data[-1]
    return {}

@app.get("/history")
def get_history(limit: int = 200):
    return sensor_data[-limit:]

@app.get("/alerts")
def get_alerts(limit: int = 50):
    return alerts[:limit]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint — client connects and receives real-time events."""
    await manager.connect(websocket)
    try:
        # Optionally send a snapshot immediately
        await websocket.send_json({"event": "snapshot", "history": sensor_data[-200:], "alerts": alerts[:50]})
        while True:
            # keep connection alive; we don't require clients to send messages.
            # If the client sends something, we ignore/echo it. This prevents the connection from closing.
            try:
                msg = await websocket.receive_text()
                # optional: clients can request things like {"cmd":"ping"}; ignore for now
            except WebSocketDisconnect:
                break
            except Exception:
                # if there is no incoming message, small sleep to avoid busy loop
                await asyncio.sleep(0.1)
    finally:
        manager.disconnect(websocket)
