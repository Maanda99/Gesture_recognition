import tensorflow as tf
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import os

# --- INT8 quantization: Stage 2, full conversion with representative dataset ---

# --- Build representative dataset (verified in Stage 1) ---
df = pd.read_csv('../Data/dataset.csv')
SAMPLES_PER_CLASS = 40
sampled = df.groupby('label').sample(n=SAMPLES_PER_CLASS, random_state=42)
X_rep = sampled.drop('label', axis=1).values.reshape(-1, 21, 3).astype(np.float32)

def representative_dataset():
    for i in range(X_rep.shape[0]):
        sample = X_rep[i:i+1]
        yield [sample]

# --- Load model and convert with quantization ---
model = load_model('../Model/gesture_cnn_model.h5')
print("Keras model loaded")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

tflite_quant_model = converter.convert()
print("Quantized conversion complete")

output_path = '../Model/gesture_cnn_model_int8.tflite'
with open(output_path, 'wb') as f:
    f.write(tflite_quant_model)

print(f"Quantized TFLite model saved to {output_path}")

# --- Compare sizes across all three versions ---
h5_size = os.path.getsize('../Model/gesture_cnn_model.h5') / 1024
tflite_size = os.path.getsize('../Model/gesture_cnn_model.tflite') / 1024
tflite_int8_size = os.path.getsize(output_path) / 1024

print(f"\nOriginal .h5 size: {h5_size:.2f} KB")
print(f"Float32 .tflite size: {tflite_size:.2f} KB")
print(f"INT8 .tflite size: {tflite_int8_size:.2f} KB")