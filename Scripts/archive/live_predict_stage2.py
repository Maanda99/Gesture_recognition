import time
import cv2
import numpy as np
import HandTrackingModule as htm

# --- Stage 2: camera + landmark extraction only, no model yet ---

def main():
    prevTime = time.time()
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector()

    printed_once = False  # only print the vector once per run, to avoid flooding console

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

            # Flatten exactly as in the collection script
            row = []
            for landmarks in relLandMarks:
                row += landmarks[1:]

            vector = np.array(row)

            if not printed_once:
                print(f"Flattened vector length: {len(row)}")
                print(f"Flattened vector shape (as np array): {vector.shape}")
                print(f"First 6 values (landmark 0 and 1): {row[:6]}")
                printed_once = True

        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)
        cv2.imshow("Hand Tracking Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()