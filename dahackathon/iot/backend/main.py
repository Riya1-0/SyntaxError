from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import random, asyncio, datetime

app = FastAPI()

# Allow frontend React (Vite) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep track of connected clients
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Simulate IoT sensor data
            data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "temperature": round(random.uniform(-20, 60), 2),
                "pressure": round(random.uniform(20, 200), 2),
                "storage": round(random.uniform(100, 1000), 2),
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)  # every 2 seconds
    except WebSocketDisconnect:
        clients.remove(websocket)
