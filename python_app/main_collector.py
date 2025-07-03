import os
import paho.mqtt.client as mqtt
import time
import json
import uuid
import socket
from pymongo import MongoClient
import mysql.connector
from neo4j import GraphDatabase


MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "mosquitto_broker")
MQTT_BROKER_PORT = 1883

MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DB")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = 3306

MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_HOST = os.environ.get("MONGO_HOST")

NEO4J_USER = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_HOST = os.environ.get("NEO4J_HOST")

mysql_conn = None
mongo_client = None
neo4j_driver = None

def connect_databases():
    global mysql_conn, mongo_client, neo4j_driver
    try:
        print(f"Connecting to MySQL at {MYSQL_HOST}:{MYSQL_PORT}...")
        mysql_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT
        )
        mysql_cursor = mysql_conn.cursor()
        mysql_cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(255),
                event_type VARCHAR(255),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data JSON
            );
        """)
        mysql_conn.commit()
        print("Connected to MySQL and table cheked.")

        print(f"Connecting to MongoDB at {MONGO_HOST}:27017...")
        mongo_client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:27017/")
        mongo_client.list_database_names()
        print("Connected to MongoDB.")

        print(f"Connecting to Neo4j at {NEO4J_HOST}:7687...")
        uri = f"bolt://{NEO4J_HOST}:7687"
        neo4j_driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
        neo4j_driver.verify_connectivity()
        print("Connected to Neo4j.")
    except Exception as e:
        print(f"Error connecting to databases: {e}")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"connected to MQTT Broker: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        connect_databases()
        client.subscribe("home/security/#")
    else:
        print(f"Failed to connect, return code: {rc}\n")

def on_message(client, userdata, msg):
    print(f"Received message : Topic: '{msg.topic}', Payload: '{msg.payload.decode()}'")
    try:
        payload_data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        payload_data = {"raw_payload": msg.payload.decode()}

    if msg.topic.startswith("home/security/door/"):
        if mysql_conn:
            try:
                mysql_cursor = mysql_conn.cursor()
                device_id = msg.topic.split("/")[-1]
                event_type = payload_data.get("status","unknown_door_event")
                mysql_cursor.execute(
                    "insert into security_events (device_id, event_type, data) VALUES (%s, %s, %s)",
                    (device_id, event_type, json.dumps(payload_data))
                )
                mysql_conn.commit()
                mysql_cursor.close()
                print(f"Stored door event in MYSQL: {device_id} - {event_type}")
            except Exception as db_e:
                print(f"Error storing in MYSQL: {db_e}")
        else:
            print("MySQL connection not established.")
    elif msg.topic.startswith("home/security/motion/"):
        if mongo_client:
            try:
                db = mongo_client.security_data
                collection = db.motion_events
                event = {
                    "topic": msg.topic,
                    "payload": payload_data,
                    "timestamp": time.time()
                }
                collection.insert_one(event)
                print(f"Stored motion event in MongoDB: {msg.topic}")
            except Exception as db_e:
                print(f"Error storing in MongoDB: {db_e}")
        else:
            print("MongoDB connection not established.")

    elif msg.topic.startswith("home/security/alarm_system"):
        if neo4j_driver:
            try:
                alarm_id = payload_data.get("alarm_id")
                triggered_devices = payload_data.get("triggered_devices", [])
                timestamp = payload_data.get("timestamp", time.time())

                with neo4j_driver.session() as session:
                    session.execute_write(
                        lambda tx: tx.run(
                            """
                            MERGE (a:Alarm {id: $alarm_id})
                            ON CREATE SET a.timestamp = $timestamp, a.status = $status
                            WITH a
                            UNWIND $triggered_devices AS device_id
                            MERGE (d:Device {id: device_id})
                            CREATE (a)-[:TRIGGERED]->(d)
                            """,
                            alarm_id=alarm_id, timestamp=timestamp, status=payload_data.get("status"),
                            triggered_devices=triggered_devices
                        )
                    )
                print(f"Stored alarm event in Neo4j: {alarm_id}")
            except Exception as db_e:
                print(f"Error storing in Neo4j: {db_e}")
        else:
            print("Neo4j connection not established.")

    else:
        print("Unhandled topic, not storing.")



hostname = socket.gethostname()
unique_suffix = uuid.uuid4().hex[:4]
client_id = f"home_security_collector_{hostname}_{unique_suffix}"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id)
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Attempting to connect to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    client.loop_start()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("KeyboardInterrupt detected. Shutting down gracefully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    client.loop_stop()
    if mysql_conn:
        mysql_conn.close()
        print("MySQL connection closed.")
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")
    if neo4j_driver:
        neo4j_driver.close()
        print("Neo4j connection closed.")
    print('MQTT Client Disconnected')
