import numpy as np
from tensorflow.keras.models import load_model

# --- Stage 1: load model + label classes only, verify before adding camera ---

model = load_model('../Model/gesture_cnn_model.h5')
print("Model loaded successfully")
model.summary()

classes = np.load('label_classes.npy', allow_pickle=True)
print(f"Label classes loaded: {classes}")
print(f"Number of classes: {len(classes)}")

# Sanity check: does a dummy input of the right shape produce a valid prediction?
dummy_input = np.zeros((1, 21, 3))  # batch of 1, matches (21,3) reshape
prediction = model.predict(dummy_input)
print(f"Dummy prediction shape: {prediction.shape}")
print(f"Dummy prediction values: {prediction}")

predicted_index = np.argmax(prediction)
predicted_name = classes[predicted_index]
print(f"Dummy predicted index: {predicted_index}")
print(f"Dummy predicted gesture name: {predicted_name}")