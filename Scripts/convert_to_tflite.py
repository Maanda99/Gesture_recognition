import tensorflow as tf
from tensorflow.keras.models import load_model
import os

# --- TFLite conversion: Stage 1, basic conversion, no optimization yet ---

model = load_model('../Model/gesture_cnn_model.h5')
print("Keras model loaded")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
print("Conversion complete")

output_path = '../Model/gesture_cnn_model.tflite'
with open(output_path, 'wb') as f:
    f.write(tflite_model)

print(f"TFLite model saved to {output_path}")

# Verify: compare file sizes between .h5 and .tflite
h5_size = os.path.getsize('../Model/gesture_cnn_model.h5') / 1024
tflite_size = os.path.getsize(output_path) / 1024
print(f"Original .h5 size: {h5_size:.2f} KB")
print(f"Converted .tflite size: {tflite_size:.2f} KB")