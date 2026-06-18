import time
import cv2
import mediapipe as mp
import HandTrackingModule as htm

class collectData():
    def __init__(self):
        print("Collect data")


def main():
    prevTime = time.time()
    cap = cv2.VideoCapture(0)

    # Create class instance
    detector = htm.handDetector()

    while True:
        success, img = cap.read()

        if not success:
            print("Failed to grap video frame")
            break

        # Process the frame and draw lines
        img = detector.findHand(img, draw=True)

        # Extract coordinates and draw dots
        landmarklist, landMarksNorm = detector.findPos(img)

        # Print the wrist position (ID 0) to console if detected
        if len(landmarklist) != 0:
            # print(f"Wrist Coordinates: {landMarksNorm[0]}")
            relLandMarks = detector.findRelative(landMarksNorm)

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

    print(success)


if __name__ == "__main__":
    main()