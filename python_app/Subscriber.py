import json

import paho.mqtt.client as mqtt
from config import MQTT_BROKER_PORT,MQTT_BROKER_HOST,MQTT_TOPIC_ROOT
from DamageAnalyzer import analyze_sensor_data_and_trigger_claim
from db_manager import store_sensor_data, init_dbs, neo4j_manager

MQTT_SUBCRIBER_TOPIC = f"{MQTT_TOPIC_ROOT}/+/+/sensor"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} with result code {str(rc)}")
        client.subscribe(MQTT_SUBCRIBER_TOPIC)
        print(f"Subscribed to topic: {MQTT_SUBCRIBER_TOPIC}")
    else:
        print(f"Connection failed with result code: {str(rc)}")

def on_message(client, userdata, msg):
    print(f"Received message - topic : {msg.topic}")
    try:
        payload_str = msg.payload.decode("utf-8")
        sensor_data = json.loads(payload_str)

        if not all(k in sensor_data for k in ["sensor_id", "type", "value", "timestamp"]):
            print(f"Warning: Incomplete sensor data received from {msg.topic}. Skipping processing.")
            print(f"Payload: {sensor_data}")
            return

        store_sensor_data(msg.topic, sensor_data)
#         todo analyse sensor data function
        analyze_sensor_data_and_trigger_claim(msg.topic,sensor_data)


    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON payload from topic {msg.topic}. Payload: {msg.payload.decode('utf-8')}")
    except UnicodeDecodeError:
        print(f"Error: Could not decode payload as UTF-8 from topic {msg.topic}.")
    except Exception as e:
        print(f"An unexpected error occurred while processing message from {msg.topic}: {e}")

if __name__ == "__main__":
    init_dbs()
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("Attempting to connect to MQTT broker...")
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        print("MQTT client connected. Starting loop...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nMQTT client stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An error occurred in the MQTT client loop: {e}")
    finally:
        if neo4j_manager:
            neo4j_manager.close()
        print("Application gracefully shutting down...")





