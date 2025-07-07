from pymongo import MongoClient
import datetime

class MongodbDbManager:
    def __init__(self,host,port,dbName,sensor_collection_name,username=None, password=None, auth_source='admin'):
        self.host = host
        self.port = port
        self.dbName = dbName
        self.sensor_collection_name = sensor_collection_name
        self.username = username
        self.password = password
        self.auth_source = auth_source

    def get_client(self):
        try:
            if self.username and self.password:
                uri = (f"mongodb://{self.username}:{self.password}"f"@{self.host}:{self.port}/{self.dbName}"f"?authSource={self.auth_source}")
                client = MongoClient(uri)
            else:
                client = MongoClient(self.host, self.port)
            return client
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return None

    def insert_sensor_data(self,topic,sensor_data):
        client = self.get_client()
        if client:
            try:
                db = client[self.dbName]
                collection = db[self.sensor_collection_name]
                sensor_data["_mqtt_topic"] = topic
                sensor_data["_received_at"] = datetime.datetime.now()
                if "timestamp" in sensor_data and isinstance(sensor_data["timestamp"], (int, float)):
                    sensor_data["timestamp"] = datetime.datetime.fromtimestamp(sensor_data["timestamp"])

                result = collection.insert_one(sensor_data)
            except Exception as e:
                print(f"Error inserting into MongoDB: {e}")
            finally:
                client.close()