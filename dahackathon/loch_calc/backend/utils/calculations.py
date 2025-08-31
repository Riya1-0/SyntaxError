import math
import config.settings as cfg

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def calculate_lcoh(distance_km,
                   electricity_cost=cfg.ELECTRICITY_COST,
                   water_cost=cfg.WATER_COST):
    elec = electricity_cost * cfg.ELECTRICITY_KWH_PER_KG
    water = water_cost * cfg.WATER_L_PER_KG
    transport = distance_km * cfg.TRANSPORT_COST_PER_KM
    return elec + water + transport  # $/kg
