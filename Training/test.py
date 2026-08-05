import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


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















