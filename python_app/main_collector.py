import paho.mqtt.client as mqtt
import time
import json
import uuid
import socket

MQTT_BROKER_HOST = "mosquitto_broker"
MQTT_BROKER_PORT = 1883

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"connected to MQTT Broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        client.subscribe("home/security/#")
    else:
        print(f"Failed to connect, return code: {rc}\n")

def on_message(client, userdata, msg):
    print(f"Received message : Topic: '{msg.topic}', Payload: '{msg.payload.decode()}'")
    pass

hostname = socket.gethostname()
unique_suffix = uuid.uuid4().hex[:4]
client_id = f"home_security_collector_{hostname}_{unique_suffix}"

client = mqtt.Client(mqtt.CallbackAPIVersion.Version1,client_id)
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Attemting to connect to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    client.loop_forever()
except Exception as e:
    print(f"An Error occured :{e}")