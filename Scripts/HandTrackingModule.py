import time
import cv2
import mediapipe as mp

#Define a class
class handDetector():
    #Constructor with parameters: hand(static_image_mode=False, max_num_hands=2,model_complexity=1,min_detection_confidence=0.5,min_tracking_confidence=0.5))
    def __init__(self,mode=False, numHands=1, complexity=1, detCon=0.5, trackCon=0.5):
        #Initialize parameters
        self.mode = mode
        self.numHands = numHands
        self.complexity = complexity
        self.detCon = detCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.numHands, self.complexity, self.detCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHand(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(img_rgb)

        if self.result.multi_hand_landmarks:
            for handLms in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    #Method to get the landmarks coordinates/pixels
    def findPos(self, img, handNo=0):
        landMarkList = []
        landMarksNorm = []  # normalised landmarks list

        if self.result.multi_hand_landmarks:
            # Check if requested hand index exists
            if len(self.result.multi_hand_landmarks) > handNo:
                myhand = self.result.multi_hand_landmarks[handNo]
                for id, landMarks in enumerate(myhand.landmark):
                    h, w, c = img.shape

                    cx, cy, cz = landMarks.x, landMarks.y, landMarks.z
                    # print(id, cx, cy, cz)
                    landMarksNorm.append([id, cx, cy, cz])

                    # Change coordinates to pixels
                    cx, cy = int(landMarks.x * w), int(landMarks.y * h)
                    # print(id, cx, cy)
                    landMarkList.append([id, cx, cy])

                    # if draw:
                    #     cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

        return landMarkList, landMarksNorm


    def findRelative(self, landMarksNorm):
        relLandMarks = []

        wrist = landMarksNorm[0]
        wrist_x, wrist_y, wrist_z = wrist[1:]

        # landMarksNorm[id, x, y, z]
        for id, rel in enumerate(landMarksNorm):
            # extract the rest of the inner list left after id
            point_x, point_y, point_z = rel[1], rel[2], rel[3]

            # Calculate point position relative to wrist
            rel_x = point_x - wrist_x
            rel_y = point_y - wrist_y
            rel_z = point_z - wrist_z

            # print(id, rel_x, rel_y, rel_z)

            relLandMarks.append([id, rel_x, rel_y, rel_z])

        return relLandMarks

def main():
    prevTime = time.time()
    cap = cv2.VideoCapture(0)

    #Create class instance
    detector = handDetector()

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