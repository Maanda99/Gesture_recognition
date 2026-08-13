import tensorflow as tf

# --- TFLite conversion: Stage 2, inspect interpreter input/output details ---

interpreter = tf.lite.Interpreter(model_path='../../Model/gesture_cnn_model.tflite')
interpreter.allocate_tensors()
print("Interpreter loaded and tensors allocated")

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("\n--- Input details ---")
print(input_details)

print("\n--- Output details ---")
print(output_details)

print(f"\nInput shape: {input_details[0]['shape']}")
print(f"Input dtype: {input_details[0]['dtype']}")
print(f"Output shape: {output_details[0]['shape']}")
print(f"Output dtype: {output_details[0]['dtype']}")