import time
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
from collections import deque, Counter
import HandTrackingModule as htm
import subprocess


# --- INT8 TFLite live gesture prediction (deployment-ready, no Keras comparison) ---

BUFFER_SIZE = 7  # number of recent predictions to smooth over
WIDTH, HEIGHT = 640, 480
FRAME_SIZE = WIDTH * HEIGHT * 3 // 2  # YUV420 planar size

def start_camera():
    cmd = [
        "rpicam-vid",
        "-t", "0",
        "--codec", "yuv420",
        "--width", str(WIDTH),
        "--height", str(HEIGHT),
        "--framerate", "30",
        "--nopreview",
        "-o", "-",
    ]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=FRAME_SIZE * 4)

def read_frame(proc):
    raw = proc.stdout.read(FRAME_SIZE)
    if len(raw) < FRAME_SIZE:
        return False, None
    yuv = np.frombuffer(raw, dtype=np.uint8).reshape((HEIGHT * 3 // 2, WIDTH))
    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
    return True, bgr


def main():
    # Load TFLite interpreter + labels once, before the camera loop starts
    interpreter = Interpreter(model_path='../Model/gesture_cnn_model_int8.tflite')
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    classes = np.load('../Training/label_classes.npy', allow_pickle=True)
    print("INT8 TFLite interpreter loaded and tensors allocated")

    prevTime = time.time()
    cam_proc = start_camera()
    detector = htm.handDetector()

    prediction_buffer = deque(maxlen=BUFFER_SIZE)
    displayed_gesture = "..."
    
    #cv2.namedWindow("Hand Tracking Video", cv2.WINDOW_NORMAL)
    #cv2.resizeWindow("Hand Tracking Video", 1280, 960)
    
    while True:
        success, img = read_frame(cam_proc)
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

        cv2.putText(img, f"Gesture: {displayed_gesture}", (10
                                                               , 120), cv2.FONT_HERSHEY_PLAIN,
                    3, (0, 0, 255), 3)

        cv2.imshow("Hand Tracking Video", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam_proc.terminate()
    cam_proc.wait()

if __name__ == "__main__":
    main()
