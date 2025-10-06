"""
Meteor Impact Predictor - Interactive Terminal Tool
--------------------------------------
- User enters meteor parameters (diameter, velocity, distance, lat/lon)
- Predicts impact consequences at specific Earth coordinates
- Calculates risk factor, damage area, mass, crater size, and casualties
- Provides detailed mitigation strategies based on location
- Saves predictions to CSV log
Author: NASA Space Apps Challenge (Meteor Madness)
"""

import math
import csv
import os
from datetime import datetime

# -----------------------------
# GEOLOCATION DATABASE (Major World Cities)
# -----------------------------
MAJOR_CITIES = {
    # North America
    "New York, USA": (40.7128, -74.0060, 8_336_817),
    "Los Angeles, USA": (34.0522, -118.2437, 3_979_576),
    "Chicago, USA": (41.8781, -87.6298, 2_693_976),
    "Houston, USA": (29.7604, -95.3698, 2_320_268),
    "Phoenix, USA": (33.4484, -112.0740, 1_680_992),
    "Philadelphia, USA": (39.9526, -75.1652, 1_584_064),
    "San Antonio, USA": (29.4241, -98.4936, 1_547_253),
    "San Diego, USA": (32.7157, -117.1611, 1_423_851),
    "Dallas, USA": (32.7767, -96.7970, 1_343_573),
    "San Jose, USA": (37.3382, -121.8863, 1_021_795),
    "Seattle, USA": (47.6062, -122.3321, 753_675),
    "Denver, USA": (39.7392, -104.9903, 715_522),
    "Boston, USA": (42.3601, -71.0589, 692_600),
    "Miami, USA": (25.7617, -80.1918, 467_963),
    "Las Vegas, USA": (36.1699, -115.1398, 641_903),
    "Toronto, Canada": (43.6532, -79.3832, 2_930_000),
    "Montreal, Canada": (45.5017, -73.5673, 1_780_000),
    "Vancouver, Canada": (49.2827, -123.1207, 675_218),
    "Mexico City, Mexico": (19.4326, -99.1332, 9_209_944),
    "Guadalajara, Mexico": (20.6597, -103.3496, 1_495_189),
    
    # South America
    "São Paulo, Brazil": (-23.5505, -46.6333, 12_325_232),
    "Rio de Janeiro, Brazil": (-22.9068, -43.1729, 6_748_000),
    "Buenos Aires, Argentina": (-34.6037, -58.3816, 3_075_646),
    "Lima, Peru": (-12.0464, -77.0428, 9_752_000),
    "Bogotá, Colombia": (4.7110, -74.0721, 7_412_566),
    "Santiago, Chile": (-33.4489, -70.6693, 5_614_000),
    "Caracas, Venezuela": (10.4806, -66.9036, 2_923_959),
    
    # Europe
    "London, UK": (51.5074, -0.1278, 8_982_000),
    "Paris, France": (48.8566, 2.3522, 2_161_000),
    "Berlin, Germany": (52.5200, 13.4050, 3_769_495),
    "Madrid, Spain": (40.4168, -3.7038, 3_223_334),
    "Rome, Italy": (41.9028, 12.4964, 2_872_800),
    "Amsterdam, Netherlands": (52.3676, 4.9041, 821_752),
    "Vienna, Austria": (48.2082, 16.3738, 1_911_191),
    "Warsaw, Poland": (52.2297, 21.0122, 1_790_658),
    "Stockholm, Sweden": (59.3293, 18.0686, 975_551),
    "Athens, Greece": (37.9838, 23.7275, 664_046),
    "Moscow, Russia": (55.7558, 37.6173, 12_506_468),
    "Istanbul, Turkey": (41.0082, 28.9784, 15_462_452),
    "Kyiv, Ukraine": (50.4501, 30.5234, 2_967_360),
    
    # Asia
    "Tokyo, Japan": (35.6762, 139.6503, 13_960_000),
    "Beijing, China": (39.9042, 116.4074, 21_540_000),
    "Shanghai, China": (31.2304, 121.4737, 27_058_480),
    "Mumbai, India": (19.0760, 72.8777, 12_442_373),
    "Delhi, India": (28.7041, 77.1025, 16_753_235),
    "Bangalore, India": (12.9716, 77.5946, 8_443_675),
    "Seoul, South Korea": (37.5665, 126.9780, 9_776_000),
    "Bangkok, Thailand": (13.7563, 100.5018, 10_539_000),
    "Singapore": (1.3521, 103.8198, 5_685_807),
    "Manila, Philippines": (14.5995, 120.9842, 1_780_148),
    "Jakarta, Indonesia": (-6.2088, 106.8456, 10_562_088),
    "Karachi, Pakistan": (24.8607, 67.0011, 14_910_352),
    "Tehran, Iran": (35.6892, 51.3890, 8_693_706),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753, 7_676_654),
    "Dubai, UAE": (25.2048, 55.2708, 3_331_420),
    "Hong Kong": (22.3193, 114.1694, 7_496_981),
    
    # Africa
    "Cairo, Egypt": (30.0444, 31.2357, 9_500_000),
    "Lagos, Nigeria": (6.5244, 3.3792, 14_862_000),
    "Johannesburg, South Africa": (-26.2041, 28.0473, 5_635_127),
    "Nairobi, Kenya": (-1.2864, 36.8172, 4_397_073),
    "Kinshasa, DR Congo": (-4.4419, 15.2663, 14_342_000),
    "Casablanca, Morocco": (33.5731, -7.5898, 3_359_818),
    "Addis Ababa, Ethiopia": (9.0320, 38.7469, 3_352_000),
    
    # Oceania
    "Sydney, Australia": (-33.8688, 151.2093, 5_312_163),
    "Melbourne, Australia": (-37.8136, 144.9631, 5_078_193),
    "Brisbane, Australia": (-27.4698, 153.0251, 2_560_720),
    "Perth, Australia": (-31.9505, 115.8605, 2_125_114),
    "Auckland, New Zealand": (-36.8485, 174.7633, 1_571_718),
}

# -----------------------------
# IMPACT SIMULATOR
# -----------------------------
def simulate_meteor_impact(diameter_m, velocity_km_s, distance_km, lat, lon, angle_deg=45, density_kg_m3=3000):
    EARTH_DENSITY = 2700  # kg/m³ (crustal rock)
    TNT_EQUIVALENT_J = 4.184e15  # 1 megaton TNT = 4.184e15 J
    MAX_DISTANCE_KM = 1e7  # 10 million km

    radius_m = diameter_m / 2
    velocity_m_s = velocity_km_s * 1000
    angle_rad = math.radians(angle_deg)
    
    # Calculate mass
    mass_kg = (4/3) * math.pi * radius_m**3 * density_kg_m3
    
    # Calculate impact energy
    energy_j = 0.5 * mass_kg * velocity_m_s**2 * math.sin(angle_rad)
    energy_mt = energy_j / TNT_EQUIVALENT_J
    
    # Calculate crater size
    crater_diameter_m = 1.161 * ((mass_kg**(1/3)) * (velocity_m_s**0.44)) / (EARTH_DENSITY**0.22)
    crater_diameter_m *= (math.sin(angle_rad))**0.33
    
    # Calculate damage radius (blast wave, thermal radiation, shockwave)
    damage_radius_km = (crater_diameter_m / 1000) * 20
    
    # Calculate proximity risk factor (closer = higher risk)
    proximity_risk = min(100, max(0, (MAX_DISTANCE_KM - distance_km) / 1e5))
    
    # Calculate impact risk factor
    if energy_mt < 0.01:
        impact_risk = 5
    elif energy_mt < 1:
        impact_risk = min(50, 20 + damage_radius_km)
    elif energy_mt < 1000:
        impact_risk = min(80, 50 + damage_radius_km * 0.5)
    else:
        impact_risk = min(100, 80 + damage_radius_km * 0.1)
    
    # Combined risk factor (proximity + impact potential)
    combined_risk = (proximity_risk * 0.4 + impact_risk * 0.6)
    combined_risk = round(min(100, max(0, combined_risk)), 1)
    
    # Impact classification
    if energy_mt < 0.01:
        impact_class = "Small fireball — harmless airburst"
        casualty_estimate = "0-10 (minor injuries from debris)"
    elif energy_mt < 1:
        impact_class = "Tunguska-scale regional event"
        casualty_estimate = "100s-1,000s (within 50km radius)"
    elif energy_mt < 1000:
        impact_class = "City to country-scale devastation"
        casualty_estimate = "10,000s-100,000s (regional catastrophe)"
    else:
        impact_class = "Global catastrophic impact"
        casualty_estimate = "Millions to billions (mass extinction event)"
    
    # Find nearest city
    nearest_city, city_distance_km = find_nearest_city(lat, lon)
    
    # Determine if city is in danger zone
    city_affected = city_distance_km <= damage_radius_km
    
    return {
        "mass_kg": mass_kg,
        "impact_energy_j": energy_j,
        "impact_energy_mt": energy_mt,
        "crater_diameter_m": crater_diameter_m,
        "damage_radius_km": damage_radius_km,
        "proximity_risk": proximity_risk,
        "impact_risk": impact_risk,
        "combined_risk_factor": combined_risk,
        "impact_classification": impact_class,
        "casualty_estimate": casualty_estimate,
        "nearest_city": nearest_city,
        "city_distance_km": city_distance_km,
        "city_affected": city_affected
    }

# -----------------------------
# GEOLOCATION HELPER
# -----------------------------
def find_nearest_city(lat, lon):
    """Find the nearest major city to impact coordinates"""
    min_distance = float('inf')
    nearest = "Unknown location"
    
    for city, (city_lat, city_lon, population) in MAJOR_CITIES.items():
        # Haversine formula for distance
        R = 6371  # Earth radius in km
        dlat = math.radians(city_lat - lat)
        dlon = math.radians(city_lon - lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(city_lat)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        if distance < min_distance:
            min_distance = distance
            nearest = city
    
    return nearest, round(min_distance, 2)

# -----------------------------
# MITIGATION STRATEGIES
# -----------------------------
def get_mitigation_strategy(risk_factor, city_affected, nearest_city, damage_radius_km):
    if risk_factor < 20:
        strategy = f"""[LOW RISK] - Airburst Alert Protocol
        
This meteor will likely burn up in the atmosphere or cause minimal ground damage.
However, residents near {nearest_city} should be aware of potential:
- Sonic booms and shockwaves
- Bright flashes in the sky
- Minor debris fallout

RECOMMENDED ACTIONS:
* Issue public awareness notice about atmospheric entry
* Monitor trajectory for any deviations
* Prepare emergency services for possible minor injuries
* Secure loose objects and windows within 50km of predicted airburst
* Educate public about meteor phenomena to prevent panic"""

    elif risk_factor < 50:
        strategy = f"""[MODERATE RISK] - Regional Evacuation Required
        
This meteor poses significant regional risk. The impact zone extends {damage_radius_km:.1f} km from the impact site.
{'[WARNING]: ' + nearest_city + ' is within the danger zone!' if city_affected else 'Nearest city (' + nearest_city + ') is outside immediate danger zone.'}

RECOMMENDED ACTIONS:
* Evacuate all residents within {damage_radius_km:.1f} km of impact coordinates
* Establish emergency shelters at least {damage_radius_km * 1.5:.1f} km away
* Deploy emergency response teams and medical units
* Secure critical infrastructure (hospitals, power plants, water systems)
* Issue emergency broadcasts and alerts
* Prepare for blast wave damage, fires, and potential tsunamis (if ocean impact)
* Coordinate with national disaster management agencies"""

    elif risk_factor < 80:
        strategy = f"""[HIGH RISK] - National Emergency & Infrastructure Protection
        
This is a catastrophic-scale impact that will devastate {damage_radius_km:.1f} km radius.
{'[CRITICAL]: ' + nearest_city + ' faces total destruction!' if city_affected else 'Major cities within ' + str(int(damage_radius_km)) + 'km must evacuate immediately!'}

RECOMMENDED ACTIONS:
* Declare national emergency and activate all disaster protocols
* Mass evacuation of population within {damage_radius_km * 2:.1f} km
* Reinforce critical infrastructure outside the impact zone
* Deploy military assets for rescue and recovery operations
* Establish emergency government continuity plans
* Stockpile food, water, and medical supplies
* Prepare for long-term displacement of millions
* International aid coordination with UN and neighboring countries
* Consider deflection missions if detection is early enough"""

    else:
        strategy = f"""[EXTREME RISK] - Global Catastrophe & Planetary Defense
        
This is an extinction-level impact event with global consequences.
ALL major population centers including {nearest_city} are at risk from global effects.

RECOMMENDED ACTIONS:
* Activate international planetary defense protocols immediately
* Consider kinetic impactor or nuclear deflection missions
* Global evacuation and shelter-in-place orders
* Prepare for:
  - Massive earthquakes and tsunamis worldwide
  - Global firestorms and atmospheric ignition
  - Impact winter and crop failures
  - Collapse of civilization infrastructure
* Establish underground shelters and seed vaults
* Preserve critical knowledge and technology
* International cooperation for human species survival
* Launch emergency space missions if time permits
* Document and preserve cultural heritage

NOTE: If impact is imminent and deflection impossible, focus on:
  - Protecting genetic diversity and knowledge repositories
  - Deep underground shelter construction
  - Long-term survival preparation for post-impact world"""

    return strategy

# -----------------------------
# INTERACTIVE PREDICTOR
# -----------------------------
def interactive_predictor(csv_filename="meteor_predictions_log.csv"):
    print("\n" + "="*70)
    print("METEOR IMPACT PREDICTOR - NASA Space Apps Challenge")
    print("="*70)
    print("\nEnter meteor parameters to predict impact consequences:\n")

    try:
        diameter_m = float(input("Meteor diameter (meters): "))
        velocity_km_s = float(input("Velocity (km/s): "))
        distance_km = float(input("Distance from Earth (km): "))
        lat = float(input("Impact latitude (-90 to 90): "))
        lon = float(input("Impact longitude (-180 to 180): "))
        
        # Validate inputs
        if not (-90 <= lat <= 90):
            print("ERROR: Invalid latitude! Must be between -90 and 90.")
            return
        if not (-180 <= lon <= 180):
            print("ERROR: Invalid longitude! Must be between -180 and 180.")
            return
        if diameter_m <= 0 or velocity_km_s <= 0 or distance_km < 0:
            print("ERROR: Invalid values! All measurements must be positive.")
            return
            
    except ValueError:
        print("ERROR: Invalid input. Please enter numeric values.")
        return

    # Run simulation
    result = simulate_meteor_impact(diameter_m, velocity_km_s, distance_km, lat, lon)
    
    # Get mitigation strategy
    mitigation = get_mitigation_strategy(
        result['combined_risk_factor'],
        result['city_affected'],
        result['nearest_city'],
        result['damage_radius_km']
    )
    
    # Display results
    print("\n" + "="*70)
    print("IMPACT PREDICTION RESULTS")
    print("="*70)
    print(f"\n[IMPACT LOCATION]")
    print(f"   Coordinates: {lat}, {lon}")
    print(f"   Nearest City: {result['nearest_city']} ({result['city_distance_km']:.2f} km away)")
    print(f"   City in Danger Zone: {'[ALERT] YES - EVACUATE IMMEDIATELY!' if result['city_affected'] else 'No - Outside damage radius'}")
    
    print(f"\n[METEOR CHARACTERISTICS]")
    print(f"   Diameter: {diameter_m:,.1f} m")
    print(f"   Velocity: {velocity_km_s:,.2f} km/s")
    print(f"   Distance from Earth: {distance_km:,.0f} km")
    print(f"   Estimated Mass: {result['mass_kg']:,.2e} kg ({result['mass_kg']/1000:,.0f} metric tons)")
    
    print(f"\n[IMPACT CONSEQUENCES]")
    print(f"   Impact Energy: {result['impact_energy_mt']:.2e} Megatons TNT")
    print(f"   Crater Diameter: {result['crater_diameter_m']:,.1f} m")
    print(f"   Damage Radius: {result['damage_radius_km']:,.1f} km")
    print(f"   Impact Classification: {result['impact_classification']}")
    print(f"   Estimated Casualties: {result['casualty_estimate']}")
    
    print(f"\n[RISK ASSESSMENT]")
    print(f"   Proximity Risk: {result['proximity_risk']:.1f}/100")
    print(f"   Impact Risk: {result['impact_risk']:.1f}/100")
    print(f"   Combined Risk Factor: {result['combined_risk_factor']:.1f}/100")
    
    print(f"\n[MITIGATION STRATEGY]")
    print(mitigation)
    
    print("\n" + "="*70)
    
    # Save to CSV log
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            header = ["Timestamp", "Diameter_m", "Velocity_km_s", "Distance_km", "Latitude", "Longitude",
                     "Mass_kg", "Impact_Energy_MT", "Crater_Diameter_m", "Damage_Radius_km",
                     "Combined_Risk_Factor", "Impact_Classification", "Nearest_City", 
                     "City_Distance_km", "City_Affected", "Casualty_Estimate"]
            writer.writerow(header)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([
            timestamp, diameter_m, velocity_km_s, distance_km, lat, lon,
            result['mass_kg'], result['impact_energy_mt'], result['crater_diameter_m'],
            result['damage_radius_km'], result['combined_risk_factor'],
            result['impact_classification'], result['nearest_city'],
            result['city_distance_km'], result['city_affected'], result['casualty_estimate']
        ])
    
    print(f"Prediction saved to {csv_filename}\n")

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    while True:
        interactive_predictor()
        user_choice = input("\nPress ENTER to predict another impact, or type 'Q' to quit: ").strip().upper()
        if user_choice == 'Q':
            print("\nThank you for using Meteor Impact Predictor!")
            print("Stay safe and keep watching the skies!\n")
            break