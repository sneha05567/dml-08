import json
import time
import uuid
from kafka import KafkaProducer
import pandas as pd
from datetime import datetime
from constants import *

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Load Test Data for Predictions
df = pd.read_csv('data/test-data/test_microsoft_stock.csv')

def send_stock_data(n=20):
    for _, row in df.head(n).iterrows():
        message = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": row["Volume"]
        }
        producer.send(INPUT_TOPIC, value=message)
        print(f"Sent: {message}")
        time.sleep(1.5) # Simulate real-time streaming

if __name__ == "__main__":
    send_stock_data()
    producer.flush()
    producer.close()
