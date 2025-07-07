import os

MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "mosquitto_broker")
MQTT_BROKER_PORT = 1883
MQTT_TOPIC_ROOT = "home"

MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "example")
MYSQL_DB = os.environ.get("MYSQL_DB")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_SENSOR_TABLE = "sensor_readings"
MYSQL_CLAIMS_TABLE = "insurance_claims"
MYSQL_PORT = 3306

MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "example")
MONGO_HOST = os.environ.get("MONGO_HOST", "mongo_db")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "home_sensor_data")
MONGO_SENSOR_COLLECTION = os.environ.get("MONGO_SENSOR_COLLECTION", "raw_sensor_data")

NEO4J_HOST = os.environ.get("NEO4J_HOST", "neo4j")
NEO4J_PORT = int(os.environ.get("NEO4J_PORT", 7687))
NEO4J_URI = f"bolt://{NEO4J_HOST}:{NEO4J_PORT}"
NEO4J_USER = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")


