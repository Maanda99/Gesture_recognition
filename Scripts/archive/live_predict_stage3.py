import time
import cv2
import numpy as np
from collections import deque, Counter
from tensorflow.keras.models import load_model
import HandTrackingModule as htm

# --- Stage 3: full live gesture prediction with majority-vote smoothing ---

BUFFER_SIZE = 7  # number of recent predictions to smooth over

def main():
    # Load model + labels once, before the camera loop starts
    model = load_model('../../Model/gesture_cnn_model.h5')
    classes = np.load('../../Training/label_classes.npy', allow_pickle=True)
    print("Model and label classes loaded")

    prevTime = time.time()
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector()

    prediction_buffer = deque(maxlen=BUFFER_SIZE)
    displayed_gesture = "..."  # shown when no hand / buffer not yet full

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

            vector = np.array(row).reshape(1, 21, 3)  # batch of 1, matches training shape

            prediction = model.predict(vector, verbose=0)
            predicted_index = np.argmax(prediction)
            predicted_name = classes[predicted_index]

            prediction_buffer.append(predicted_name)

            # Majority vote over the buffer
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

        cv2.putText(img, f"Gesture: {displayed_gesture}", (700, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 255, 0), 3)

        cv2.imshow("Hand Tracking Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()