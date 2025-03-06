import os

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
INPUT_TOPIC = "input-data"
OUTPUT_TOPIC = "predictions"

# Model Paths
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "stock_predictor.keras")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
Y_SCALER_PATH = os.path.join(MODEL_DIR, "y_scaler.pkl")

# Output Directory
OUTPUT_DIR = "output"
CSV_FILE = os.path.join(OUTPUT_DIR, "stock_predictions.csv")

# Ensure necessary directories exist
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
