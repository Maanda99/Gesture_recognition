import threading
import time
import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter
from collections import deque, Counter
import HandTrackingModule as htm
import subprocess
import paho.mqtt.client as mqtt
import smart_bulb as smb
import logging

logging.getLogger("PyP100.PyP100").setLevel(logging.CRITICAL)


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

#  ------------------------------------------------ MQTT ------------------------------------------------
MQTT_BROKER = "localhost"   # Mosquitto running on this same Pi
MQTT_PORT = 1883

TOPIC_FAN = "home/esp32/fanSpeed"
TOPIC_RELAY = "home/esp32/relay"
TOPIC_GESTURE = "home/esp32/gesture"

ACTION_GESTURES = {"thumbs_up", "thumbs_down", "okay", "open_palm", "fist", "peace", "point"}

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("Connected to MQTT broker")
    else:
        print(f"MQTT connect failed, reason code: {reason_code}")



bulb_state = {"bulb": None, "busy": False, "last": 0}

def _worker():
    try:
        bulb_state["bulb"] = smb.connect_to_bulb()
        print("Bulb Connected")
    except Exception as e:
        print(f"Bulb unreachable: {e}")
    bulb_state["busy"] = False

def get_bulb_connection(bulb):
    if bulb is not None:
        return bulb
    if bulb_state["bulb"] is not None:
        return bulb_state["bulb"]
    if not bulb_state["busy"] and time.time() - bulb_state["last"] > 30:
        bulb_state["busy"] = True
        bulb_state["last"] = time.time()
        threading.Thread(target=_worker, daemon=True).start()
    return None


def publish_gesture_action(client, gesture):
    client.publish(TOPIC_GESTURE, gesture, qos=1, retain=False)
    if gesture == "thumbs_up":
        client.publish(TOPIC_FAN, "increase", qos=1, retain=False)
        print("Increase fan speed")
    elif gesture == "thumbs_down":
        client.publish(TOPIC_FAN, "decrease", qos=1, retain=False)
        print("Decrease fan speed")
    elif gesture == "okay":
        client.publish(TOPIC_RELAY, "toggle", qos=1, retain=False)
        print("Relay toggle")
    elif gesture in ("open_palm", "fist", "peace"):
        print(f"Smart Bulb '{gesture}' triggers PyP100 action")
    elif gesture == "point":
        print("Smart Bulb toggle")


def main():
    # Load TFLite interpreter + labels once, before the camera loop starts
    interpreter = Interpreter(model_path='../Model/gesture_cnn_model_int8.tflite')
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    classes = np.load('../Training/label_classes.npy', allow_pickle=True)
    print("INT8 TFLite interpreter loaded and tensors allocated")

    # MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pi5-gesture-publisher")
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    mqtt_client.loop_start()
   
    fired_gesture = None   # tracks what's already been published for the current hold

    candidate_gesture = None
    candidate_start_time = None
    confirm_seconds = 1.0

    prevTime = time.time()
    cam_proc = start_camera()
    detector = htm.handDetector()

    

    prediction_buffer = deque(maxlen=BUFFER_SIZE)
    displayed_gesture = "..."

    try:
        bulb = smb.connect_to_bulb()
    except Exception as e:
        print(f"Bulb unreachable. Reason: {e}")
        bulb = None

    colour_index = 0  
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

            if (most_common != candidate_gesture):
                candidate_gesture = most_common
                candidate_start_time = time.time()
                displayed_gesture = "..."
            
            else:
                if(time.time() - candidate_start_time >= confirm_seconds):
                    displayed_gesture = candidate_gesture
            
                    if displayed_gesture in ACTION_GESTURES and displayed_gesture != fired_gesture:
                        if (len(prediction_buffer) == BUFFER_SIZE):
                            publish_gesture_action(mqtt_client, displayed_gesture)
                            fired_gesture = displayed_gesture
                            
                            if(fired_gesture == "open_palm"):
                                bulb = get_bulb_connection(bulb)
                                if bulb is not None:
                                    try:
                                        current_brightness = bulb.getDeviceInfo()['brightness']
                                        new_brightness = current_brightness + 20
                                        new_brightness =  min(new_brightness, 100)
                                        bulb.setBrightness(new_brightness)
                                    except Exception as e:
                                        print("Bulb unreachable")
                                        bulb = None


                            elif(fired_gesture == "fist"):
                                bulb = get_bulb_connection(bulb)
                                if bulb is not None:
                                    try:
                                        current_brightness = bulb.getDeviceInfo()['brightness']
                                        new_brightness = current_brightness - 20
                                        new_brightness =  max(new_brightness, 1)
                                        bulb.setBrightness(new_brightness)
                                    except Exception as e:
                                        print("Bulb unreachable")
                                        bulb = None


                            elif(fired_gesture == "peace"):
                                bulb = get_bulb_connection(bulb)
                                if bulb is not None:
                                    try:
                                        hue, sat = smb.COLOUR_CYCLE[colour_index]
                                        bulb.setColor(hue, sat)
                                        colour_index = (colour_index + 1)%len(smb.COLOUR_CYCLE)
                                    except Exception as e:
                                        print("Bulb unreachable")
                                        bulb = None


                            elif(fired_gesture == "point"):
                                bulb = get_bulb_connection(bulb)
                                if bulb is not None:
                                    try:
                                        bulb.toggleState() 
                                    except Exception as e:
                                        print("Bulb unreachable")
                                        bulb = None


        else:
            prediction_buffer.clear()
            displayed_gesture = "..."
            fired_gesture = None   # hand left frame — next hold of same gesture can fire again
            candidate_gesture = None
            candidate_start_time = None


        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        cv2.putText(img, f"Gesture: {displayed_gesture}", (10, 120), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

        cv2.imshow("Gesture Recognition System", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    cam_proc.terminate()
    cam_proc.wait()

if __name__ == "__main__":
    main()
