#Generated with assistance from Artificial Intelligence - Claude
"""
Meteor Data Collector + Risk & Mitigation (NEO, Fireball, CAD)
"""

import math
import csv
import os
import time
from datetime import datetime, timedelta, timezone
import json

try:
    import requests
except ImportError:
    print("⚠️ Install 'requests': pip install requests")
    exit()

API_KEY = "GjbT7BRsxhQQaJ5kJTYcAk7u0IaRgWAAMaS4dg9y"
CSV_FILE = "meteor_data_combined.csv"
MAX_DISTANCE_KM = 1e7  # 10 million km

MITIGATION_STRATEGIES = [
    "Early detection and orbit monitoring to plan deflection.",
    "Evacuation of high-risk areas if impact is imminent.",
    "International coordination for disaster management.",
    "Deploy kinetic impactor to change asteroid trajectory.",
    "Use nuclear devices only as last-resort deflection.",
    "Public alert system for meteor airburst warnings.",
    "Secure critical infrastructure in potential impact zones.",
    "Simulation drills for cities under high risk.",
    "Satellite observation to track fragmenting meteors.",
    "Emergency medical preparation for blast injuries.",
    "Fire suppression readiness in case of fireball impacts.",
    "Marine alerts for potential tsunami from ocean impacts.",
    "Reinforcement of buildings against shockwaves.",
    "Debris shielding for satellites in orbit.",
    "Rapid response teams for search & rescue.",
    "Meteor insurance programs for property damage.",
    "Temporary exclusion zones around predicted impact sites.",
    "Analysis of meteor composition for chemical hazards.",
    "Post-impact environmental monitoring plans.",
    "Research into long-term planetary defense strategies."
]

def calculate_risk_factor(diameter, velocity, distance_km):
    energy = 0.5 * (4/3 * math.pi * (diameter/2)**3 * 3000) * (velocity*1000)**2
    energy_mt = energy / 4.184e15
    risk = min(100, max(0, energy_mt * 0.5 + (MAX_DISTANCE_KM - distance_km)/1e5))
    return round(risk, 1)

def choose_mitigation(risk):
    index = min(len(MITIGATION_STRATEGIES)-1, int(risk / 5))
    return MITIGATION_STRATEGIES[index]

# NEO
def fetch_neo(start_date, end_date):
    current = start_date
    neos = []
    while current < end_date:
        chunk_end = min(current + timedelta(days=7), end_date)
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={current.strftime('%Y-%m-%d')}&end_date={chunk_end.strftime('%Y-%m-%d')}&api_key={API_KEY}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            for day in data.get("near_earth_objects", {}):
                for obj in data["near_earth_objects"][day]:
                    ca = obj["close_approach_data"][0]
                    dist_km = float(ca["miss_distance"]["kilometers"])
                    if dist_km <= MAX_DISTANCE_KM:
                        neos.append({
                            "source": "NEO",
                            "name": obj["name"],
                            "diameter_m": float(obj["estimated_diameter"]["meters"]["estimated_diameter_max"]),
                            "velocity_km_s": float(ca["relative_velocity"]["kilometers_per_second"]),
                            "distance_km": dist_km
                        })
        except Exception as e:
            print(f"Error fetching NEOs {current} to {chunk_end}: {e}")
        current = chunk_end + timedelta(days=1)
        time.sleep(1)
    return neos

# Fireball
def fetch_fireball(start_date, end_date):
    url = f"https://ssd-api.jpl.nasa.gov/fireball.api?date-min={start_date.strftime('%Y-%m-%d')}&date-max={end_date.strftime('%Y-%m-%d')}"
    fireballs = []
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        for event in data.get("data", []):
            try:
                diam = float(event[7]) if event[7] not in ["", None] else 1.0
                vel = float(event[4]) if event[4] not in ["", None] else 0.0
                dist = float(event[1]) if event[1] not in ["", None] else MAX_DISTANCE_KM
                if dist <= MAX_DISTANCE_KM:
                    fireballs.append({
                        "source": "Fireball",
                        "name": event[0],
                        "diameter_m": diam,
                        "velocity_km_s": vel,
                        "distance_km": dist
                    })
            except:
                continue
    except Exception as e:
        print(f"Error fetching Fireballs: {e}")
    return fireballs

# CAD (Close Approach Data)
def fetch_cad(start_date, end_date):
    cad_list = []
    # CAD API uses a different format - single query for entire date range
    url = f"https://ssd-api.jpl.nasa.gov/cad.api?date-min={start_date.strftime('%Y-%m-%d')}&date-max={end_date.strftime('%Y-%m-%d')}&dist-max={MAX_DISTANCE_KM/149597870.7:.4f}"  # Convert km to AU
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        
        # CAD API returns data in a different format with 'fields' and 'data'
        fields = data.get("fields", [])
        if not fields:
            print("No fields returned from CAD API")
            return cad_list
            
        # Find indices for the fields we need
        try:
            des_idx = fields.index("des")  # designation
            dist_idx = fields.index("dist")  # distance in AU
            v_rel_idx = fields.index("v_rel")  # relative velocity in km/s
            h_idx = fields.index("h") if "h" in fields else None  # absolute magnitude
        except ValueError as e:
            print(f"Missing required field in CAD response: {e}")
            return cad_list
        
        for row in data.get("data", []):
            try:
                dist_au = float(row[dist_idx])
                dist_km = dist_au * 149597870.7  # Convert AU to km
                
                if dist_km <= MAX_DISTANCE_KM:
                    # Estimate diameter from absolute magnitude if available
                    diameter = 1.0  # default
                    if h_idx is not None and row[h_idx]:
                        try:
                            H = float(row[h_idx])
                            # Approximate diameter from absolute magnitude (assuming albedo = 0.14)
                            diameter = 1329 / math.sqrt(0.14) * 10**(-0.2 * H)
                        except:
                            pass
                    
                    cad_list.append({
                        "source": "CAD",
                        "name": row[des_idx],
                        "diameter_m": diameter,
                        "velocity_km_s": float(row[v_rel_idx]),
                        "distance_km": dist_km
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error fetching CAD data: {e}")
    
    return cad_list

# MAIN
def main():
    end_date = datetime.now(timezone.utc).replace(tzinfo=None)
    start_date = end_date - timedelta(days=150)

    print("Fetching NEO data...")
    neos = fetch_neo(start_date, end_date)
    print(f"NEO objects fetched: {len(neos)}")

    print("Fetching Fireball data (last 2 years)...")
    fireball_start = end_date - timedelta(days=730)  # 2 years for better fireball coverage
    fireballs = fetch_fireball(fireball_start, end_date)
    print(f"Fireballs fetched: {len(fireballs)}")

    print("Fetching CAD data...")
    cad_objects = fetch_cad(start_date, end_date)
    print(f"CAD objects fetched: {len(cad_objects)}")

    all_objects = neos + fireballs + cad_objects
    for obj in all_objects:
        obj["risk_factor"] = calculate_risk_factor(obj["diameter_m"], obj["velocity_km_s"], obj["distance_km"])
        obj["mitigation_strategy"] = choose_mitigation(obj["risk_factor"])

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "name", "diameter_m", "velocity_km_s", "distance_km", "risk_factor", "mitigation_strategy"])
        writer.writeheader()
        for obj in all_objects:
            writer.writerow(obj)
    print(f"CSV saved: {CSV_FILE}")

if __name__ == "__main__":
    main()