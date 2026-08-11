import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import load_model

df = pd.read_csv('../Data/test_dataset.csv')
print(f"Total number of rows and columns = {df.shape}")
print(df['label'].value_counts())

# Features - flat, no reshape needed for the dense model
X = df.drop('label', axis=1)

# Labels - reuse the SAME encoding as training
label_encoder = LabelEncoder()
label_encoder.classes_ = np.load('label_classes.npy', allow_pickle=True)
integer_labels = label_encoder.transform(df['label'])
y_true = to_categorical(integer_labels, num_classes=7)

# Load the already-trained dense model - no training here
dense_model = load_model('../Model/gesture_model.h5')

loss, accuracy = dense_model.evaluate(X, y_true)
print(f"\n[Fresh Test Set - Dense] Loss: {loss:.4f} | Accuracy: {accuracy:.4f}")