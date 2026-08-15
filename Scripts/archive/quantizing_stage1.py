import pandas as pd
import numpy as np

# --- INT8 quantization: Stage 1, verify stratified representative sampling ---

df = pd.read_csv('../../Data/dataset.csv')
print(f"Full dataset shape: {df.shape}")
print(f"Gesture counts in full dataset:\n{df['label'].value_counts()}")

SAMPLES_PER_CLASS = 40
sampled = df.groupby('label').sample(n=SAMPLES_PER_CLASS, random_state=42)

print(f"\nSampled dataset shape: {sampled.shape}")
print(f"Gesture counts in sampled dataset:\n{sampled['label'].value_counts()}")

# Split features from label, same as training scripts
X_rep = sampled.drop('label', axis=1).values.reshape(-1, 21, 3).astype(np.float32)
print(f"\nRepresentative X shape: {X_rep.shape}")
print(f"Representative X dtype: {X_rep.dtype}")


def representative_dataset():
    for i in range(X_rep.shape[0]):
        sample = X_rep[i:i+1]  # keep batch dimension: shape (1, 21, 3)
        yield [sample]


# Verify the generator produces correctly shaped output
gen = representative_dataset()
first_sample = next(gen)
print(f"\nFirst yielded sample type: {type(first_sample)}")
print(f"First yielded sample[0] shape: {first_sample[0].shape}")
print(f"First yielded sample[0] dtype: {first_sample[0].dtype}")

# Count total samples the generator will produce
count = sum(1 for _ in representative_dataset())
print(f"\nTotal samples generator will yield: {count}")