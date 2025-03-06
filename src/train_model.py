import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import os

from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from constants import MODEL_PATH, SCALER_PATH, Y_SCALER_PATH

# Load Data
df = pd.read_csv("data/microsoft_stock.csv")

# Select Features & Target
FEATURES = ["Open", "High", "Low", "Close", "Volume"]
TARGET = "Close"

X = df[FEATURES].values
y = df[TARGET].values.reshape(-1, 1)  # Reshape for scaler

# Normalize Data
X_scaler = MinMaxScaler()
X_scaled = X_scaler.fit_transform(X)

y_scaler = MinMaxScaler()
y_scaled = y_scaler.fit_transform(y)

# Build Model
model = keras.Sequential([
    keras.layers.Dense(64, activation="relu", input_shape=(X.shape[1],)),
    keras.layers.Dense(32, activation="relu"),
    keras.layers.Dense(16, activation="relu"),
    keras.layers.Dense(1)  # Regression Output
])

model.compile(optimizer="adam", loss="mse")

# Train Model
model.fit(X_scaled, y_scaled, epochs=100, batch_size=32, validation_split=0.1)

# Ensure models directory exists
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Save Model & Scalers
model.save(MODEL_PATH)
joblib.dump(X_scaler, SCALER_PATH)
joblib.dump(y_scaler, Y_SCALER_PATH)

print("Model Trained & Saved Successfully")
