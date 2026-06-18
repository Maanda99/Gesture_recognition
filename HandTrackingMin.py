import time

import cv2
import mediapipe as mp

# Use local machine camera, 0 is usually first camera available
cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

prevTime = 0
currTime = 0

while True:
    success, img = cap.read()

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    result = hands.process(img_rgb)

    # print(result.multi_hand_landmarks)

    if success:

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

        currTime = time.time()
        fps = 1/(currTime-prevTime)
        prevTime=currTime

        cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 255, 255), 3)
        cv2.imshow("Hand Tracking Video", img)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()

print(success)