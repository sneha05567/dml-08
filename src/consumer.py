import json
import joblib
import numpy as np
import os
import time
import pandas as pd
import logging
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from tensorflow import keras
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

# Import constants
from constants import *

# Setup logging
LOG_FILE = "logs/prediction_logs.log"
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# Load Pre-trained Model & Scalers
model = keras.models.load_model(MODEL_PATH)
x_scaler = joblib.load(SCALER_PATH)
y_scaler = joblib.load(Y_SCALER_PATH)  # Load Y scaler
print(f"\n\nTrained Model loaded from {MODEL_PATH}, \nScalers loaded from {SCALER_PATH}, {Y_SCALER_PATH}")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Kafka Consumer
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
)

# Open CSV File for Logging
with open(CSV_FILE, "w") as f:
    f.write("id,timestamp,open,high,low,volume,close,predicted_close\n")

print(f"\nConsumer is listening to topic {INPUT_TOPIC}...")

# Store actual and predicted values for evaluation
actual_values = []
predicted_values = []
message_count = 0

def log_performance_metrics():
    if len(actual_values) >= 10:
        mse = mean_squared_error(actual_values, predicted_values)
        mae = mean_absolute_error(actual_values, predicted_values)
        mape = mean_absolute_percentage_error(actual_values, predicted_values)
        logging.info(f"Metrics after {len(actual_values)} messages - MSE: {mse:.4f}, MAE: {mae:.4f}, MAPE: {mape:.4f}")

for message in consumer:
    start_time = time.time()  # Start time for latency measurement
    data = message.value
    input_features = np.array([[data["open"], data["high"], data["low"], data["close"], data["volume"]]])

    # Scale input
    input_scaled = x_scaler.transform(input_features)

    # Predict scaled close price
    predicted_scaled = model.predict(input_scaled)

    # **Inverse transform to get actual close price**
    predicted_close = y_scaler.inverse_transform(predicted_scaled.reshape(-1, 1))[0][0]

    # Store for evaluation
    actual_values.append(data["close"])
    predicted_values.append(predicted_close)
    message_count += 1

    # Calculate latency
    latency = time.time() - start_time

    # Prepare output message
    prediction_msg = {
        "id": data["id"],
        "timestamp": datetime.now().isoformat(),
        "open": data["open"],
        "high": data["high"],
        "low": data["low"],
        "volume": data["volume"],
        "close": data["close"],
        "predicted_close": float(predicted_close),
        "latency": latency
    }

    # Save to CSV
    with open(CSV_FILE, "a") as f:
        f.write(f'{prediction_msg["id"]},{prediction_msg["timestamp"]},{prediction_msg["open"]},'
                f'{prediction_msg["high"]},{prediction_msg["low"]},{prediction_msg["volume"]},'
                f'{prediction_msg["close"]},{prediction_msg["predicted_close"]}\n')

    # Log information
    logging.info(f"Processed Message ID: {data['id']}, Latency: {latency:.4f} seconds, Total Messages: {message_count}")
    
    # Log performance metrics every 10 messages
    if message_count % 10 == 0:
        log_performance_metrics()

    # Send prediction to Kafka topic
    producer.send(OUTPUT_TOPIC, value=prediction_msg)
    print(f"Predicted & Sent to predictions topic: {prediction_msg}")
