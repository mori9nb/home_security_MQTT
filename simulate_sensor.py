#!/usr/bin/env python3
import time
import random
import datetime
import json

import paho.mqtt.client as mqtt

from python_app.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC_ROOT

def publish_sensor_data(sensor_id, sensor_type, value, location):
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        topic = f"{MQTT_TOPIC_ROOT}/{location}/{sensor_id}/sensor"
        payload = {
            "sensor_id": sensor_id,
            "type": sensor_type,
            "value": value,
            "timestamp": datetime.datetime.utcnow().timestamp()
        }
        client.publish(topic, json.dumps(payload))
        print(f"[PUBLISH] {topic} → {json.dumps(payload)}")
    except Exception as e:
        print(f"[ERROR] publishing to {topic}: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    print("🔄 Starting sensor data simulation...")


    publish_sensor_data("temp_kitchen_001", "temperature", 22.5, "kitchen")
    time.sleep(1)
    publish_sensor_data("humidity_bathroom_001", "humidity", 65.2, "bathroom")
    time.sleep(1)
    publish_sensor_data("smoke_hall_001", "smoke_detector", False, "hallway")
    time.sleep(1)
    publish_sensor_data("door_front_001", "door_contact", False, "entryway")
    time.sleep(1)


    print("⚠️  Minor water leak in bathroom")
    publish_sensor_data("water_leak_001", "water_leak", True, "bathroom")
    time.sleep(2)


    print("🌡️  Temperature rising in kitchen")
    for temp in (35.0, 45.0):
        publish_sensor_data("temp_kitchen_001", "temperature", temp, "kitchen")
        time.sleep(1)
    time.sleep(1)


    print("🔥  Fire detected in hallway")
    publish_sensor_data("smoke_hall_001", "smoke_detector", True, "hallway")
    time.sleep(1)
    publish_sensor_data("temp_hall_001", "temperature", 105.0, "hallway")
    time.sleep(2)


    print("🏗️  Medium structural stress in basement")
    publish_sensor_data("struct_basement_001", "structural_stress",
                        {"level": "medium", "vibration_hz": 5.2}, "basement")
    time.sleep(2)


    print("⚠️  Re-triggering water leak (major?)")
    publish_sensor_data("water_leak_001", "water_leak", True, "bathroom")
    time.sleep(2)


    print("🏗️  High structural stress in basement")
    publish_sensor_data("struct_basement_001", "structural_stress",
                        {"level": "high", "vibration_hz": 8.1}, "basement")
    time.sleep(2)


    print("🌙  Random temperature fluctuations in bedroom")
    for _ in range(5):
        temp_val = round(random.uniform(18.0, 26.0), 1)
        sid = f"temp_bedroom_00{random.randint(1,2)}"
        publish_sensor_data(sid, "temperature", temp_val, "bedroom")
        time.sleep(random.uniform(0.5, 1.5))

    print("✅ Sensor data simulation complete.")
