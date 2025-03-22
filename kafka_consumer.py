from flask import Flask
import threading
from confluent_kafka import Consumer
import json
from datetime import datetime
from db_utils import insert_data, modify_data, fetch_data

app = Flask(__name__)  # Fake web server to bind a port on Render

@app.route("/")
def home():
    return "✅ Kafka Consumer is running!"

# --- Existing code moved into functions below ---

def read_config():
    config = {}
    with open("client.properties") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config

def process_message(message):
    try:
        data = json.loads(message)
        ecg = data.get("ecg")
        respiration = data.get("respiration")
        temperature = data.get("temperature")

        if None in [ecg, respiration, temperature]:
            print("⚠️ Invalid data received, skipping...")
            return

        sql_query = """
        SELECT patientid, smartshirtid 
        FROM smartshirt 
        WHERE shirtstatus = TRUE
        LIMIT 1
        """
        result = fetch_data(sql_query)

        if not result:
            print("⚠️ No active SmartShirt found, skipping...")
            return

        patient_id = result["patientid"]
        smartshirt_id = result["smartshirtid"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        sensor_data = {
            "timestamp": timestamp,
            "ecg": ecg,
            "respiration": respiration,
            "temperature": temperature,
            "patientID": patient_id,
            "smartshirtID": smartshirt_id
        }

        insert_data("health_vitals", sensor_data)

        sql_insert = """
        INSERT INTO health_vitals (timestamp, ecg, respiration_rate, temperature, patientid, smartshirtid) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        modify_data(sql_insert, (timestamp, ecg, respiration, temperature, patient_id, smartshirt_id))

        print(f"✅ Data inserted for patient {patient_id}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")

def consume_from_kafka():
    config = read_config()
    config["group.id"] = "sensor-consumer-group"
    config["auto.offset.reset"] = "earliest"

    consumer = Consumer(config)
    consumer.subscribe(["sensor-data"])

    print("🚀 Kafka Consumer started. Listening for sensor data...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                key = msg.key().decode("utf-8") if msg.key() else "N/A"
                value = msg.value().decode("utf-8")
                print(f"📩 Received: {value}")
                process_message(value)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Kafka Consumer...")
    finally:
        consumer.close()

# --- Start Kafka in thread, and web server for Render ---
if __name__ == "__main__":
    threading.Thread(target=consume_from_kafka).start()
    app.run(host="0.0.0.0", port=10000)
