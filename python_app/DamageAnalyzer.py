

import datetime
import uuid
from db_manager import neo4j_manager, mysql_db_manager

def estimate_damage_cost(damage_type, severity_indicators):
    """
    Estimates the cost of damage based on type and severity indicators.
    This is a simplified rule-based model.
    """
    cost = 0
    damage_details = {}

    if damage_type == "water_leak":

        if severity_indicators.get("duration_minutes", 0) > 60 or \
                severity_indicators.get("flow_rate", 0) > 10: # Hypothetical metrics
            cost = 5000.00
            damage_details = {"type": "Water Damage (Major)", "description": "Prolonged or high-volume leak causing significant damage."}
        else:
            cost = 500.00
            damage_details = {"type": "Water Damage (Minor)", "description": "Small, contained leak, likely localized."}
    elif damage_type == "fire":

        if severity_indicators.get("smoke_density", 0) > 0.8 or \
                severity_indicators.get("temp_peak", 0) > 100:
            cost = 25000.00
            damage_details = {"type": "Fire Damage (Significant)", "description": "High smoke density or extreme heat, indicating substantial fire."}
        else:
            cost = 5000.00
            damage_details = {"type": "Fire Damage (Minor)", "description": "Smoke detected, potential small fire or smoke-related issue."}
    elif damage_type == "structural_stress":
        if severity_indicators.get("level") == "high":
            cost = 100000.00
            damage_details = {"type": "Structural Damage (Severe)", "description": "High stress detected in key structural area, major repair needed."}
        elif severity_indicators.get("level") == "medium":
            cost = 20000.00
            damage_details = {"type": "Structural Damage (Moderate)", "description": "Medium stress detected, potential foundational or load-bearing issue."}
    else:
        cost = 0.00
        damage_details = {"type": "Unknown", "description": "No defined damage cost for this event type."}

    return cost, damage_details

def trigger_insurance_claim(sensor_id, location, damage_details, estimated_cost, timestamp_event):
    """
    Simulates triggering an insurance claim and records it in MySQL and Neo4j.
    In a real system, this would interact with an external insurance API.
    """
    claim_id = str(uuid.uuid4())
    timestamp_filed = datetime.datetime.now()

    print("\n--- Initiating Insurance Claim (Simulated) ---")
    print(f"Claim ID: {claim_id}")
    print(f"Sensor ID: {sensor_id}")
    print(f"Location: {location}")
    print(f"Damage Type: {damage_details['type']}")
    print(f"Description: {damage_details['description']}")
    print(f"Estimated Cost: ${estimated_cost:,.2f}")
    print(f"Event Timestamp: {datetime.datetime.fromtimestamp(timestamp_event).isoformat()}")
    print(f"Claim Filed At: {timestamp_filed.isoformat()}")
    print("--- Claim Sent ---\n")


    mysql_db_manager.insert_claim(
        claim_id=claim_id,
        timestamp_filed=timestamp_filed,
        damage_type=damage_details['type'],
        estimated_cost=estimated_cost,
        description=damage_details['description'],
        status="Pending Automated Review",
        sensor_id=sensor_id,
        location=location
    )


    neo4j_manager.create_damage_event(
        sensor_id=sensor_id,
        damage_type=damage_details['type'],
        estimated_cost=estimated_cost,
        description=damage_details['description'],
        timestamp=timestamp_event,
        claim_id=claim_id
    )


def analyze_sensor_data_and_trigger_claim(topic, sensor_data):
    """
    Analyzes incoming sensor data for potential damage and triggers a claim if conditions are met.
    """
    sensor_id = sensor_data.get("sensor_id")
    sensor_type = sensor_data.get("type")
    value = sensor_data.get("value")
    timestamp = sensor_data.get("timestamp")


    topic_parts = topic.split('/')
    location = topic_parts[1] if len(topic_parts) > 1 else "unknown"

    if not all([sensor_id, sensor_type, timestamp is not None, value is not None]):
        print(f"Skipping damage analysis for incomplete data: {sensor_data}")
        return

    damage_type = None
    severity_indicators = {}



    if sensor_type == "water_leak" and value is True:
        damage_type = "water_leak"

        severity_indicators = {"duration_minutes": 10, "flow_rate": 5}
    elif sensor_type == "smoke_detector" and value is True:
        damage_type = "fire"

        severity_indicators = {"smoke_density": 0.9, "temp_peak": 120}
    elif sensor_type == "structural_stress" and isinstance(value, dict) and "level" in value:

        if value.get("level") in ["medium", "high"]:
            damage_type = "structural_stress"
            severity_indicators = value

    if damage_type:
        estimated_cost, details = estimate_damage_cost(damage_type, severity_indicators)
        print(f"Potential damage detected from {sensor_id} ({sensor_type}) in {location}.")
        print(f"  Estimated cost: ${estimated_cost:,.2f}. Details: {details['description']}")
        trigger_insurance_claim(sensor_id, location, details, estimated_cost, timestamp)
