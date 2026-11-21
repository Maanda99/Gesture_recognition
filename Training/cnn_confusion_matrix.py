import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import load_model

df = pd.read_csv('../Data/test_dataset.csv')
print(f"Total number of rows and columns = {df.shape}")
print(df['label'].value_counts())

# Features
X = df.drop('label', axis=1)
X_cnn = X.values.reshape(-1, 21, 3)

# Labels - reuse the SAME encoding as training
label_encoder = LabelEncoder()
label_encoder.classes_ = np.load('label_classes.npy', allow_pickle=True)
integer_labels = label_encoder.transform(df['label'])
y_true = to_categorical(integer_labels, num_classes=7)

# Load the already-trained model - no training here
cnn_model = load_model('../Model/gesture_cnn_model.h5')

loss, accuracy = cnn_model.evaluate(X_cnn, y_true)
print(f"\n[Fresh Test Set - CNN] Loss: {loss:.4f} | Accuracy: {accuracy:.4f}")
print()

y_pred = np.argmax(cnn_model.predict(X_cnn), axis=1)
cm = confusion_matrix(integer_labels, y_pred)
classes = np.load('label_classes.npy', allow_pickle=True)
ConfusionMatrixDisplay(cm, display_labels=classes).plot(xticks_rotation=45)
plt.savefig("confusion_matrix.png", dpi=300, bbox_inches="tight")