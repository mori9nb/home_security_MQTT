import json

import mysql.connector
import datetime

class MySQLDatabaseManager:
    def __init__(self, host, user, password, database, sensor_table, claims_table):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.sensor_table = sensor_table
        self.claims_table = claims_table
        self.conn = None
        self.cursor = None

    def connect(self, use_database=True):
        if use_database:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        else:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        self.cursor = self.conn.cursor()
        return self.conn

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_database(self):
        self.connect(use_database=False)
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        self.close()

    def create_tables(self):
        self.connect()
        sensor_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.sensor_table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME,
                topic VARCHAR(255),
                sensor_id VARCHAR(255),
                sensor_type VARCHAR(255),
                value JSON,
                location VARCHAR(255),
                received_at DATETIME
            )
        """
        self.cursor.execute(sensor_table_query)

        claims_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self.claims_table} (
                claim_id VARCHAR(255) PRIMARY KEY,
                timestamp_filed DATETIME,
                damage_type VARCHAR(255),
                estimated_cost DECIMAL(10, 2),
                description TEXT,
                status VARCHAR(50),
                sensor_id VARCHAR(255),
                location VARCHAR(255)
            )
        """
        self.cursor.execute(claims_table_query)

        self.conn.commit()
        self.close()

    def initialize(self):
        try:
            self.create_database()
            self.create_tables()
            print("MySQL database and tables initialized successfully.")
        except mysql.connector.Error as err:
            print(f"Error initializing MySQL: {err}")


    def insert_sensor_data(self, topic, sensor_data):
        try:
            conn = self.connect()
            cursor = conn.cursor()

            topic_parts = topic.split('/')
            location = topic_parts[1] if len(topic_parts) > 1 else "unknown"

            sql = f"""
                INSERT INTO {self.sensor_table} (timestamp, topic, sensor_id, sensor_type, value, location, received_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                datetime.datetime.fromtimestamp(sensor_data.get("timestamp")),
                topic,
                sensor_data.get("sensor_id"),
                sensor_data.get("type"),
                json.dumps(sensor_data.get("value")),
                location,
                datetime.datetime.now()
            )
            cursor.execute(sql, values)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error inserting sensor data into MySQL: {err}")

    def insert_claim(self, claim_id, timestamp_filed, damage_type, estimated_cost, description, status, sensor_id, location):
        try:
            conn = self.connect()
            cursor = conn.cursor()

            sql = f"""
                INSERT INTO {self.claims_table} (claim_id, timestamp_filed, damage_type, estimated_cost, description, status, sensor_id, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                claim_id,
                timestamp_filed,
                damage_type,
                estimated_cost,
                description,
                status,
                sensor_id,
                location
            )
            cursor.execute(sql, values)
            conn.commit()
            conn.close()
            print(f"Claim {claim_id} inserted into MySQL successfully.")
        except mysql.connector.Error as err:
            print(f"Error inserting claim into MySQL: {err}")
