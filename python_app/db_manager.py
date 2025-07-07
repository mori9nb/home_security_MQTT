from config import (
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_SENSOR_TABLE, MYSQL_CLAIMS_TABLE,
    MONGO_HOST, MONGO_PORT, MONGO_DATABASE, MONGO_SENSOR_COLLECTION,
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, MONGO_USER, MONGO_PASSWORD,
)
from MysqlDatabaseManager import MySQLDatabaseManager
from MongoDbManager import MongodbDbManager
from Neo4jManager import Neo4jManager

mysql_db_manager = MySQLDatabaseManager(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    sensor_table=MYSQL_SENSOR_TABLE,
    claims_table=MYSQL_CLAIMS_TABLE
)
mongo_manager = MongodbDbManager(
    host=MONGO_HOST,
    port=MONGO_PORT,
    dbName =MONGO_DATABASE,
    sensor_collection_name=MONGO_SENSOR_COLLECTION,
    username=MONGO_USER,
    password=MONGO_PASSWORD,
    auth_source='admin'
)
neo4j_manager = Neo4jManager(
    uri=NEO4J_URI,
    user=NEO4J_USER,
    password=NEO4J_PASSWORD
)

def store_sensor_data(topic,sensor_data):
    print(f"[STORE] topic={topic}, sensor_data={sensor_data}")

    sensor_id = sensor_data.get("sensor_id")
    sensor_type = sensor_data.get("type")
    timestamp = sensor_data.get("timestamp")
    value = sensor_data.get("value")

    topic_parts = topic.split('/')
    location = topic_parts[1] if len(topic_parts) > 1 else "unknown"
    property_id = "property_" + location.replace(" ", "_")
    if not all([sensor_id, sensor_type, timestamp is not None, value is not None]):
        print(f"Skipping database storage due to incomplete data: {sensor_data}")
        return
    mysql_db_manager.insert_sensor_data(topic,sensor_data)
    mongo_manager.insert_sensor_data(topic,sensor_data)
    neo4j_manager.create_sensor_node(sensor_id,sensor_type,location,property_id)
    neo4j_manager.record_sensor_event(sensor_id,timestamp,value)

def init_dbs():
    print("Initializing databases...")
    mysql_db_manager.initialize()
    print("Databases initialized successfully.")



