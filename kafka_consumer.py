from flask import Flask
import threading
from confluent_kafka import Consumer
import json
from datetime import datetime
from db_utils import modify_data, fetch_data
from pytz import timezone
import time

app = Flask(__name__)  # Fake web server to bind a port on Render

@app.route("/")
def home():
    return "✅ Kafka Consumer is running!"

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

        # Skip stale messages
        msg_time_str = data.get("timestamp")
        if msg_time_str:
            try:
                msg_time = datetime.fromisoformat(msg_time_str.replace("Z", "+00:00"))
                now = datetime.now(timezone("UTC"))
                age = (now - msg_time).total_seconds()

                if age > 150:
                    print(f"⚠️ Skipping old/stale message (age: {age:.2f} sec):", data)
                    return
            except Exception as e:
                print(f"❌ Error parsing timestamp: {e}")

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

        # Store timestamp in Pakistani time
        pakistan_time = datetime.now(timezone("Asia/Karachi"))
        timestamp = pakistan_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

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
    config["group.id"] = f"sensor-consumer-{int(time.time())}"  # Unique group to skip old offsets
    config["auto.offset.reset"] = "latest"
    config["enable.auto.commit"] = True
    config["auto.commit.interval.ms"] = 5000

    consumer = Consumer(config)
    consumer.subscribe(["sensor-data"])

    print("🚀 Kafka Consumer started. Listening for sensor data...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("⏳ No message received in this cycle...")
                continue

            if msg and msg.error() is None:
                key = msg.key().decode("utf-8") if msg.key() else "N/A"
                value = msg.value().decode("utf-8")
                print(f"📩 Received: {value}")
                process_message(value)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Kafka Consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    threading.Thread(target=consume_from_kafka).start()
    app.run(host="0.0.0.0", port=10000)
