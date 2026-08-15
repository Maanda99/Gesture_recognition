import time
import cv2
import numpy as np
import tensorflow as tf
from collections import deque, Counter
import HandTrackingModule as htm

# --- TFLite live gesture prediction (deployment-ready, no Keras comparison) ---

BUFFER_SIZE = 7  # number of recent predictions to smooth over

def main():
    # Load TFLite interpreter + labels once, before the camera loop starts
    interpreter = tf.lite.Interpreter(model_path='../Model/gesture_cnn_model.tflite')
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    classes = np.load('../Training/label_classes.npy', allow_pickle=True)
    print("TFLite interpreter loaded and tensors allocated")

    prevTime = time.time()
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector()

    prediction_buffer = deque(maxlen=BUFFER_SIZE)
    displayed_gesture = "..."

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab video frame")
            break

        img = cv2.flip(img, 1)
        img = detector.findHand(img, draw=True)
        landmarklist, landMarksNorm = detector.findPos(img)

        if len(landmarklist) != 0:
            relLandMarks = detector.findRelative(landMarksNorm)

            row = []
            for landmarks in relLandMarks:
                row += landmarks[1:]

            tflite_input = np.array(row, dtype=input_details[0]['dtype']).reshape(1, 21, 3)
            interpreter.set_tensor(input_details[0]['index'], tflite_input)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])

            predicted_index = np.argmax(output)
            predicted_name = classes[predicted_index]

            prediction_buffer.append(predicted_name)
            most_common = Counter(prediction_buffer).most_common(1)[0][0]
            displayed_gesture = most_common
        else:
            prediction_buffer.clear()
            displayed_gesture = "..."

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)

        cv2.putText(img, f"Gesture: {displayed_gesture}", (700
                                                               , 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 255, 0), 3)

        cv2.imshow("Hand Tracking Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()