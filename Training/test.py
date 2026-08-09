import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping


df = pd.read_csv('../Data/dataset.csv')
df.to_csv('output.csv', index=False) # Save dataframe to a csv file

num_rows_columns = df.shape
print(f"Total number of rows and columns = {num_rows_columns}") # Print the number of rows and columns (r, c)
print(df.head(0))

# How many unique labels exist and how many rows per gesture
num_Labels = df['label'].unique()
num_rows_per_gesture = df['label'].value_counts()
print(f"Number of unique labels = {num_Labels}")
print(f"Number of rows per gesture = {num_rows_per_gesture}")

# ________________________________________________________________________________________
print("________________________________________________________________________________________")

# Converting string labels to integers
label_encoder = LabelEncoder()
integer_labels = label_encoder.fit_transform(df['label'])

# Converting integers to one-hot vectors
one_hot_labels = to_categorical(integer_labels)

# Print statements to verify everything
print(f"Classes found (in order): {label_encoder.classes_}")
print(f"First 5 string labels: {df['label'].values[:5]}")
print(f"First 5 integer labels: {integer_labels[:5]}")
print(f"First 5 one-hot label:\n {one_hot_labels[:5]}")
print(f"One-hot shape: {one_hot_labels.shape}")


# ________________________________________________________________________________________
print("________________________________________________________________________________________")
# Features = landmark columns only, Labels = one_hot_labels
X = df.drop('label', axis=1)
y = one_hot_labels

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size= 0.2,
    stratify= one_hot_labels,
    random_state=42
)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)

# ________________________________________________________________________________________
print("________________________________________________________________________________________")

# Constructing the architecture based on the list of gestures

model = Sequential([
    # Layer 1: The input
    # 128 hidden neurons with ReLU and 63 features
    Dense(128, activation='relu', input_shape=(63,)),

    # Layer 2: Dropout at 30% rate
    Dropout(0.3),

    # Layer 3: 64 hidden neurons with ReLU
    Dense(64, activation='relu'),

    # Layer 4: Dropout at 30% rate
    Dropout(0.3),

    # Layer 5: Output with 7 neurons and Softmax
    Dense(7, activation='softmax')
])
#printing the overview and parameter metrics
model.summary()


model.compile(
    optimizer= 'adam',
    loss= 'categorical_crossentropy',
    metrics= ['accuracy']
)

print("Model compiled successfully")


early_stop = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.2,   # carved from X_train only
    callbacks=[early_stop]
)
print("Model trained successfully")

test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")
print("Model tested successfully")

model.save('../Model/gesture_model.h5')
print("Model saved successfully")

