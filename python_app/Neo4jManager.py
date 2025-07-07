from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import datetime
import json


class Neo4jManager:
    def __init__(self,uri, user, password,
                 location_label = "location",
                 property_label="Property",
                 sensor_label="Sensor",
                 sensor_event_label="SensorEvent",
                 damage_event_label="DamageEvent"):
        self._driver = None
        self.location_label = location_label
        self.property_label = property_label
        self.sensor_label = sensor_label
        self.sensor_event_label = sensor_event_label
        self.damage_event_label = damage_event_label

        try:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
            self._driver.verify_connectivity()
            print("Connected to Neo4j")
        except ServiceUnavailable as e:
            print(f" Neo4j unavailable: {e}")
            self._driver = None
        except Exception as e:
            print(f" Error connecting to Neo4j: {e}")
            self._driver = None

    def close(self):
        if self._driver:
            self._driver.close()
            print("Neo4j connection closed")

    def _execute_query(self, query, parameters = None):
        if not self._driver:
            print("Neo4j driver is not initialized.")
            return None
        try:
            with self._driver.session() as session:
                return session.run(query, parameters)
        except Exception as e:
            print(f" Error executing Neo4J query: {e}")
            return None

    def create_or_get_location(self, location_name):
        query = f"""
        MERGE (loc:{self.location_label} {{name: $location_name}})
        RETURN loc
        """
        return self._execute_query(query, {"location_name": location_name})

    def create_or_get_property(self, property_id, address=""):
        """
        Ensure a property node exists.
        """
        query = f"""
        MERGE (p:{self.property_label} {{property_id: $property_id}})
        ON CREATE SET p.address = $address
        RETURN p
        """
        return self._execute_query(query, {"property_id": property_id, "address": address})

    def create_sensor_node(self, sensor_id, sensor_type, location_name, property_id="default_property"):
        """
        Create a sensor node and link it to its location and property.
        """
        self.create_or_get_location(location_name)
        self.create_or_get_property(property_id)

        query = f"""
        MATCH (loc:{self.location_label} {{name: $location_name}})
        MATCH (prop:{self.property_label} {{property_id: $property_id}})
        MERGE (s:{self.sensor_label} {{sensor_id: $sensor_id}})
        ON CREATE SET s.type = $sensor_type
        MERGE (s)-[:LOCATED_IN]->(loc)
        MERGE (loc)-[:PART_OF]->(prop)
        RETURN s, loc, prop
        """
        return self._execute_query(query, {
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "location_name": location_name,
            "property_id": property_id
        })

    def record_sensor_event(self, sensor_id, timestamp, value, event_type="reading"):
        """
        Record a new sensor event node linked to its sensor.
        """
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.datetime.fromtimestamp(timestamp).isoformat()

        query = f"""
        MATCH (s:{self.sensor_label} {{sensor_id: $sensor_id}})
        CREATE (e:{self.sensor_event_label} {{
            timestamp: datetime($timestamp),
            value: $value,
            type: $event_type
        }})
        CREATE (s)-[:HAS_EVENT]->(e)
        RETURN e
        """
        return self._execute_query(query, {
            "sensor_id": sensor_id,
            "timestamp": timestamp,
            "value": json.dumps(value),
            "event_type": event_type
        })

    def create_damage_event(self, sensor_id, damage_type, estimated_cost, description, timestamp, claim_id=None):
        """
        Create a damage event node linked to the sensor.
        """
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.datetime.fromtimestamp(timestamp).isoformat()

        query = f"""
        MATCH (s:{self.sensor_label} {{sensor_id: $sensor_id}})
        CREATE (d:{self.damage_event_label} {{
            type: $damage_type,
            estimated_cost: $estimated_cost,
            description: $description,
            timestamp: datetime($timestamp),
            claim_id: $claim_id
        }})
        CREATE (s)-[:CAUSED]->(d)
        RETURN d
        """
        return self._execute_query(query, {
            "sensor_id": sensor_id,
            "damage_type": damage_type,
            "estimated_cost": float(estimated_cost),
            "description": description,
            "timestamp": timestamp,
            "claim_id": claim_id
        })