import time
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import HandTrackingModule as htm

# --- INT8 quantization: Stage 3, compare Keras vs INT8 TFLite predictions live ---

def main():
    # Load Keras model
    keras_model = load_model('../../Model/gesture_cnn_model.h5')
    print("Keras model loaded")

    # Load INT8 TFLite interpreter
    interpreter = tf.lite.Interpreter(model_path='../../Model/gesture_cnn_model_int8.tflite')
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("INT8 TFLite interpreter loaded and tensors allocated")
    print(f"Input dtype: {input_details[0]['dtype']}  Output dtype: {output_details[0]['dtype']}")

    # Shared label classes
    classes = np.load('../../Training/label_classes.npy', allow_pickle=True)

    prevTime = time.time()
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector()

    frame_count = 0
    match_count = 0
    MAX_COMPARISON_FRAMES = 30

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab video frame")
            break

        img = cv2.flip(img, 1)
        img = detector.findHand(img, draw=True)
        landmarklist, landMarksNorm = detector.findPos(img)

        if len(landmarklist) != 0 and frame_count < MAX_COMPARISON_FRAMES:
            relLandMarks = detector.findRelative(landMarksNorm)

            row = []
            for landmarks in relLandMarks:
                row += landmarks[1:]

            # --- Keras prediction ---
            keras_input = np.array(row).reshape(1, 21, 3)
            keras_prediction = keras_model.predict(keras_input, verbose=0)
            keras_index = np.argmax(keras_prediction)
            keras_name = classes[keras_index]

            # --- INT8 TFLite prediction ---
            tflite_input = np.array(row, dtype=input_details[0]['dtype']).reshape(1, 21, 3)
            interpreter.set_tensor(input_details[0]['index'], tflite_input)
            interpreter.invoke()
            tflite_output = interpreter.get_tensor(output_details[0]['index'])
            tflite_index = np.argmax(tflite_output)
            tflite_name = classes[tflite_index]

            # --- Compare ---
            is_match = keras_name == tflite_name
            match_count += int(is_match)
            match_label = "MATCH" if is_match else "MISMATCH"
            print(f"Frame {frame_count}: Keras={keras_name} | INT8={tflite_name} | {match_label}")

            frame_count += 1

            if frame_count == MAX_COMPARISON_FRAMES:
                print(f"\nFinal agreement: {match_count}/{MAX_COMPARISON_FRAMES} "
                      f"({100 * match_count / MAX_COMPARISON_FRAMES:.1f}%)")

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)
        cv2.putText(img, f"Comparisons: {frame_count}/{MAX_COMPARISON_FRAMES}", (10, 140),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        cv2.imshow("Hand Tracking Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()