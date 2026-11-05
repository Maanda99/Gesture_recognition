# Computer Vision Gesture Recognition System

A real-time hand gesture recognition system for touchless control of physical
devices, built as a final-year capstone project (GA11). Motivated by
accessibility use cases for non-verbal users — recognized gestures trigger a
fan, a smart bulb, and a relay-controlled device, with live status shown on
an LCD.

## Pipeline
Camera (rpicam-vid) → MediaPipe hand landmarks → TFLite INT8 CNN inference
→ gesture smoothing + confirmation buffer → MQTT (QoS1) → ESP32 (PubSubClient)
→ 20x4 I2C LCD / two-channel relay / DC fan motor

                 Raspberry Pi 5 also drives a TP-Link Tapo L530E
                 smart bulb directly over the local network (KLAP protocol)


## Recognized gestures

| Gesture      | Action                                      |
|--------------|----------------------------------------------|
| `thumbs_up`   | Increase fan speed                           |
| `thumbs_down` | Decrease fan speed                           |
| `okay`        | Toggle relay                                 |
| `open_palm`   | Increase bulb brightness (+10, capped at 100)|
| `fist`        | Decrease bulb brightness (-10, floor at 1)   |
| `peace`       | Step to next colour in bulb colour cycle     |
| `point`       | Reserved — no action assigned yet            |

## Hardware

- Raspberry Pi 5
- ESP32
- 20x4 I2C LCD
- Two-channel relay module
- DC fan motor + IRLZ44 MOSFET + 1N4007 flyback diode + adjustable buck
  module (470µF cap across buck V+/GND — required to prevent PWM-induced
  brownout resets on the ESP32; see deviations below)
- TP-Link Tapo L530E smart bulb (firmware 1.4.4, KLAP protocol)

## Software setup (Raspberry Pi)

Python 3.11.9, virtual environment at `.venv`. Key pinned dependencies:
numpy==1.26.4
opencv-contrib-python==4.11.0.86
mediapipe==0.10.18
tflite-runtime==2.14.0
paho-mqtt==2.1.0
almottier/TapoP100 (git, main branch — KLAP protocol support)
python-dotenv



### Credentials

Copy the example files and fill in real values — both are gitignored:

```bash
cp .env.example .env
```

`.env` requires:

MY_EMAIL=your_tapo_account_email
MY_PASSWORD=your_tapo_account_password
TAPO_BULB_IP=192.168.x.x



## ESP32 firmware

Arduino IDE. Subscribes to `home/esp32/fanSpeed`, `home/esp32/gesture`,
`home/esp32/relay`. Non-blocking PWM ramp for the fan (5-unit steps every
100ms via `millis()`) to avoid the ground-bounce brownout issue noted below.

### Credentials

```bash
cp secrets.h.example secrets.h
```

`secrets.h` requires:
```cpp
#define WIFI_SSID "your_network"
#define WIFI_PASSWORD "your_password"
#define MQTT_BROKER_IP "192.168.x.x"
```

## MQTT

Mosquitto broker running locally on the Pi (`listener 1883 0.0.0.0`).
Anonymous access is enabled — documented as an accepted limitation for a
closed local-network demo, not suitable for production use.

## Known limitations / documented deviations

- **LCD display simplified** to a single static screen (header, gesture,
  fan state, bulb state) rather than the originally proposed 3-mode
  scene system (Relax/Sleep/Bright), since bulb hardware installation
  and state verification were not complete in time to support it honestly.
- **Motor circuit is breadboard, not soldered** — tooling was inadequate;
  documented as a GA11 Time & Change Management deviation.
- **Bulb reconnects on every gesture trigger** rather than persisting a
  connection across the session — acceptable given negligible handshake
  latency observed in testing.
- **ESP32 MQTT client has been observed to disconnect intermittently at
  random**, self-recovering via `PubSubClient` reconnect logic. Root
  cause not fully diagnosed; suspected AP-side flakiness rather than a
  code fault, since the Pi-side client and hardware ramp logic are
  unaffected.
- **Model evaluation**: original train/test split showed inflated accuracy
  due to temporal leakage (near-duplicate frames from continuous chronological
  capture); a separately collected 700-row held-out set was used for a
  valid accuracy estimate.

## Project principle

Known limitations and scope deviations are documented explicitly rather
than suppressed. This README and the accompanying GA11 report aim to
reflect the system as it actually behaves, including its trade-offs.
