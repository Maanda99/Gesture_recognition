import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

df = pd.read_csv('../Data/dataset.csv')

print(f"Total number of rows and columns = {df.shape}")

# Features
X = df.drop('label', axis=1)
X_cnn = X.values.reshape(-1, 21, 3)

# Labels - reuse the SAME encoding as the dense model
label_encoder = LabelEncoder()
label_encoder.classes_ = np.load('label_classes.npy', allow_pickle=True)
integer_labels = label_encoder.transform(df['label'])   # transform, NOT fit_transform
y = to_categorical(integer_labels)

print(f"Classes found (in order): {label_encoder.classes_}")

# Load the SAME split the dense model used - do not create a new one here
idx_test = np.load('test_indices.npy')
idx_train = np.setdiff1d(np.arange(len(X_cnn)), idx_test)

rng = np.random.default_rng(42)
rng.shuffle(idx_train)   # shuffle in place, seeded for reproducibility

X_train_cnn = X_cnn[idx_train]
X_test_cnn = X_cnn[idx_test]
y_train_cnn = y[idx_train]
y_test_cnn = y[idx_test]

print("X_train_cnn shape:", X_train_cnn.shape)
print("X_test_cnn shape:", X_test_cnn.shape)

# CNN architecture
cnn_model = Sequential([
    Conv1D(16, kernel_size=3, activation='relu', input_shape=(21, 3)),
    Conv1D(32, kernel_size=3, activation='relu'),
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(7, activation='softmax')
])

cnn_model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = cnn_model.fit(
    X_train_cnn, y_train_cnn,
    epochs=100,
    batch_size=32,
    validation_split=0.2,
    callbacks=[early_stop]
)

test_loss, test_accuracy = cnn_model.evaluate(X_test_cnn, y_test_cnn)
print(f"\n[CNN Results] Loss: {test_loss:.4f} | Accuracy: {test_accuracy:.4f}")

cnn_model.save('../Model/gesture_cnn_model.h5')
print("CNN model saved successfully")