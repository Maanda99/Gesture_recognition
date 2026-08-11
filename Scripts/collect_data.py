import time
import cv2
import os
import csv
import HandTrackingModule as htm

def columnNames():
    columns = []
    for i in range(21):
        for axis in ['x', 'y', 'z']:
            columns.append(f"landmark_{i}{axis}")

    columns.append("label")

    return columns

def getRowCount():
    path = "../Data/test_dataset.csv"
    count = 0

    if os.path.exists(path):
        with open(path, "r") as file:
            read = csv.reader(file)

            # Skip the first row
            next(read, None)

            for row in read:
                count+=1

    return count

def saveData(data):
    path = "../Data/test_dataset.csv"

    # Check if file exists
    if os.path.exists(path):
        with open(path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print("Data saved")

    # If file does not exist, create a new file, append column names and data
    else:
        with open(path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(columnNames())
            writer.writerow(data)
            print("File Created")
            print("Data saved")


def main():
    # gesture label dict
    KEY_LABEL_MAP = {
        '1': 'open_palm',
        '2': 'fist',
        '3': 'peace',
        '4': 'thumbs_up',
        '5': 'thumbs_down',
        '6': 'point',
        '7': 'okay'
    }
    # Intialize variable
    current_gesture = None
    relLandMarks = []
    prevTime = time.time()
    rows = getRowCount()

    cap = cv2.VideoCapture(0)

    # Create class instance
    detector = htm.handDetector()

    while True:
        success, img = cap.read()

        if not success:
            print("Failed to grap video frame")
            break


        # Flip the image horizontally
        img = cv2.flip(img, 1)

        # Process the frame and draw lines
        img = detector.findHand(img, draw=True)

        # Extract coordinates and draw dots
        landmarklist, landMarksNorm = detector.findPos(img)

        # Print the wrist position (ID 0) to console if detected
        if len(landmarklist) != 0:
            # print(f"Wrist Coordinates: {landMarksNorm[0]}")
            relLandMarks = detector.findRelative(landMarksNorm)
            # print(relLandMarks[0])

        # Calculating vid frames
        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)

        cv2.putText(img, str(f"Num rows: {rows}"), (800, 70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)

        cv2.imshow("Hand Tracking Video", img)

        # Listen for keyboard input
        key = chr(cv2.waitKey(1) & 0xFF)
        if key in KEY_LABEL_MAP:
            gesture = KEY_LABEL_MAP[key]
            current_gesture = gesture
            if current_gesture != None and len(relLandMarks) != 0:
                row = []
                for landmarks in relLandMarks:
                    row += landmarks[1:]
                    # print(row)

                # Append gesture name
                row.append(current_gesture)
                print(f"Gesture: {gesture}")

                # Pass data
                saveData(row)
                rows+=1

        if key == 'q':
            break

    cap.release()
    cv2.destroyAllWindows()

    print(f"Program Successfully ran: {success}")

if __name__ == "__main__":
    main()