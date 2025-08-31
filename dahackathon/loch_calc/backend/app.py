

from fastapi import FastAPI
from pydantic import BaseModel
from math import radians, sin, cos, atan2, sqrt

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware



# Allow frontend (Vite) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:5173"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/lcoh")
def get_lcoh(lat: float, lon: float):
    # Dummy calculation (replace with real hydrogen cost model later)
    lcoh_value = round((abs(lat) + abs(lon)) / 10, 2)
    return {"latitude": lat, "longitude": lon, "lcoh": lcoh_value}


# -----------------------------
# Constants
# -----------------------------
ELECTRICITY_COST = 0.05        # $/kWh
WATER_COST = 0.002             # $/liter
TRANSPORT_COST_PER_KM = 0.1    # $/km
ELECTRICITY_KWH_PER_KG = 50    # kWh/kg H2
WATER_L_PER_KG = 9             # L/kg H2

MARKET_LOCATION = (19.0760, 72.8777)  # Mumbai

# -----------------------------
# Input model
# -----------------------------
class Site(BaseModel):
    lat: float
    lon: float

# -----------------------------
# Haversine formula
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * (2 * atan2(sqrt(a), sqrt(1 - a)))

# -----------------------------
# LCOH calculation
# -----------------------------
def calculate_lcoh(distance_km):
    elec = ELECTRICITY_COST * ELECTRICITY_KWH_PER_KG
    water = WATER_COST * WATER_L_PER_KG
    transport = distance_km * TRANSPORT_COST_PER_KM
    return elec + water + transport

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/calculate")
def get_lcoh(site: Site):
    distance = haversine(site.lat, site.lon, MARKET_LOCATION[0], MARKET_LOCATION[1])
    lcoh = calculate_lcoh(distance)
    return {
        "latitude": site.lat,
        "longitude": site.lon,
        "distance_km": round(distance, 2),
        "lcoh_usd_per_kg": round(lcoh, 2)
    }


