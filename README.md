# Computer Vision Gesture Recognition System

A real-time hand gesture recognition system for touchless control of physical devices. A camera feeds hand landmarks into a quantized CNN running on a Raspberry Pi 5, and recognised gestures are sent over MQTT to an ESP32 (relay, fan, LCD) and directly to a smart bulb.

**Motivation:** give people who can't use voice-based interfaces a non-verbal, touchless way to control technology.

---

## How it works

```
Camera → MediaPipe → CNN (TFLite INT8, Pi 5) → MQTT (Mosquitto on Pi) → ESP32 → actuators
                                      └──────→ Tapo L530E smart bulb (direct from Pi)
```

1. **Capture:** the Pi 5 camera is read through an `rpicam-vid` pipe (YUV420 frames).
2. **Landmarks:** MediaPipe extracts hand landmarks from each frame.
3. **Classification:** a 1D CNN, converted to TFLite with INT8 weight quantization, classifies the gesture.
4. **Confirmation:** a 7-frame majority vote feeds a hold timer. A gesture must be held continuously for 1.5 s before it fires, and fires once per hold.
5. **Actuation:** the Pi publishes to MQTT (QoS 1, not retained). The ESP32 drives the relay, fan and LCD. The Pi controls the bulb itself.

## Gesture mapping

| Gesture | Action |
|---|---|
| `open_palm` | Bulb brightness +10 (max 100) |
| `fist` | Bulb brightness −10 (min 1) |
| `peace` | Cycle bulb colour |
| `thumbs_up` | Fan speed up |
| `thumbs_down` | Fan speed down |
| `okay` | Toggle relay |
| `point` | Toggle bulb on/off |

## Hardware

- Raspberry Pi 5 + Pi camera
- ESP32
- TP-Link Tapo L530E smart bulb
- 20x4 I2C LCD
- 2-channel relay module
- IRLZ44 MOSFET, 1N4007 flyback diode, 470 µF decoupling capacitor
- LM2596 buck module, 12 V / 2 A supply with barrel jack breakout
- Joystick DC motor (used as the fan motor)

## Repository layout

```
HandTracking/
├── Data/           Training and held-out test datasets (CSV)
├── Training/       Dense and CNN training + evaluation scripts, label classes
├── Model/          Trained Keras and TFLite (float32 / INT8) models
├── Scripts/        Data collection, TFLite conversion, quantization, live inference
│   └── verification/   Keras vs TFLite comparison scripts
├── RaspberryPi/    Pi inference + MQTT + bulb control, bulb test script
└── ESP32/          Firmware (.ino) and secrets template
```

## Setup

### Software versions

Python 3.11 (built from source on the Pi), TensorFlow 2.15.1 / Keras 2.15.0, MediaPipe 0.10.18, TFLite runtime 2.14.0, OpenCV `opencv-contrib-python==4.11.0.86`, paho-mqtt, python-dotenv, and the `almottier/TapoP100` fork of PyP100.

> **Pin OpenCV to 4.11.0.86.** Version 5.x forces numpy ≥ 2, which breaks `tflite-runtime==2.14.0`.

> **Use the `almottier/TapoP100` fork.** The PyPI release of PyP100 only supports the legacy protocol; current bulb firmware needs KLAP.

### 1. Credentials

Credentials are gitignored. Copy the templates and fill them in:

- Raspberry Pi: copy `.env.example` to `.env` (Tapo account and bulb details)
- ESP32: copy the `secrets.h` example template to `secrets.h` (Wi-Fi and MQTT broker details)

### 2. MQTT broker (Raspberry Pi)

Install Mosquitto and add to its config:

```
listener 1883 0.0.0.0
allow_anonymous true
```

> Anonymous access is fine for a closed local demo network but is **not** secure. Enable authentication before using this anywhere else.

### 3. Run on the Pi

```bash
python RaspberryPi/pi_live_predict_tflite_int8.py
```

### 4. Flash the ESP32

Open the `.ino` in the Arduino IDE, make sure `secrets.h` sits in the same folder, then upload.

## MQTT topics

| Topic | Purpose |
|---|---|
| `home/esp32/gesture` | Current gesture shown on the LCD |
| `home/esp32/fanSpeed` | Fan speed |
| `home/esp32/relay` | Relay toggle |
| `home/esp32/lcd` | Reserved debug channel (backlight / clear), unused by the main publisher |

## Training and evaluation

- **Dataset:** 4,200 training rows and 700 held-out test rows across 7 gestures, collected in interleaved rotation to limit session drift.
- **Models:** a dense network and a 1D CNN, each exported to TFLite float32 and INT8.
- **Quantization:** INT8 is weight-only. Inputs and outputs stay float32, which suits the Pi 5's general-purpose CPU.
- **Model sizes:** CNN `.h5` ≈ 477 KB, TFLite float32 ≈ 149 KB, TFLite INT8 ≈ 42 KB.

Scripts in `Scripts/verification/` compare Keras and TFLite predictions live on a webcam.

## Known limitations and lessons learned

- **Test split:** the original test split had temporal leakage; a fresh held-out set was collected to replace it.
- **Camera on Pi 5:** raw V4L2 fails on the RP1-CFE interface (`VIDIOC_STREAMON: Invalid argument`), so frames come from an `rpicam-vid` pipe.
- **MediaPipe version:** 0.10.18 is used because no aarch64 wheel exists for 0.10.21.
- **Bulb power:** the relay must not cut mains to the smart bulb, since that drops its Wi-Fi and breaks the API connection. The relay switches secondary devices only.
- **Grounding:** a shared ground between the ESP32 and motor circuit caused brownout resets. Use separate grounds and place the decoupling capacitor across the buck module's V+/GND.
- **Motor:** a joystick DC motor stands in for the originally planned 5 V fan.
- **No authentication** on the MQTT broker (see above).

## Tech stack

Python, TensorFlow / Keras, TensorFlow Lite, MediaPipe, OpenCV, MQTT (Mosquitto, paho-mqtt), ESP32 (Arduino C++), Raspberry Pi 5.

## Author

Maanda — [@Maanda99](https://github.com/Maanda99)
