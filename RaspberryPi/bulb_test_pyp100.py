import os
import sys
import time
 
from dotenv import load_dotenv
from PyP100 import PyL530
 
load_dotenv()  # reads .env in the current working directory into os.environ
 
 
def get_required_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        sys.exit(
            f"[CONFIG ERROR] Environment variable {var_name} is not set.\n"
            f"Run: export {var_name}=\"...\" before launching this script."
        )
    return value
 
 
def connect_bulb() -> PyL530.L530:
    email = get_required_env("MY_EMAIL")
    password = get_required_env("MY_PASSWORD")
    bulb_ip = get_required_env("TAPO_BULB_IP")
 
    bulb = PyL530.L530(bulb_ip, email, password)
 
    print(f"[BULB] Handshaking with {bulb_ip} ...")
    bulb.handshake()  # sets up cookies
    print("[BULB] Logging in ...")
    bulb.login()      # sets up AES key/IV
    print("[BULB] Auth OK.")
    return bulb
 
 
def test_basic_on_off(bulb: PyL530.L530) -> None:
    print("\n--- Basic on/off test ---")
    info = bulb.getDeviceInfo()
    print(f"[BULB] Device info (nickname/state check): "
          f"on={info.get('device_on')}, model={info.get('model', '?')}")
 
    print("[BULB] turnOn()")
    bulb.turnOn()
    time.sleep(1.5)
 
    print("[BULB] setBrightness(100)")
    bulb.setBrightness(100)
    time.sleep(1.5)
 
    print("[BULB] turnOff()")
    bulb.turnOff()
    time.sleep(1.5)
 
    print("[BULB] turnOn() again for colour test to follow")
    bulb.turnOn()
 
 
# Placeholder colour cycle for the 'peace' gesture — (hue 0-360, saturation 0-100).
# This is a first pass to prove setColor() works end-to-end.
# Actual step count / palette is still an open decision (outstanding item #2).
COLOUR_CYCLE = [
    (0, 100),    # red
    (120, 100),  # green
    (240, 100),  # blue
    (280, 80),   # purple
]
 
 
def test_colour_cycle(bulb: PyL530.L530, hold_seconds: float = 2.0) -> None:
    print("\n--- Colour cycle test (setColor) ---")
    for hue, sat in COLOUR_CYCLE:
        print(f"[BULB] setColor(hue={hue}, saturation={sat})")
        bulb.setColor(hue, sat)
        time.sleep(hold_seconds)
 
 
def test_color_temp(bulb: PyL530.L530) -> None:
    print("\n--- Colour temperature test (setColorTemp) ---")
    print("[BULB] setColorTemp(2700) — warm white")
    bulb.setColorTemp(2700)
    time.sleep(2)
 
 
if __name__ == "__main__":
    bulb = connect_bulb()
 
    try:
        test_basic_on_off(bulb)
        test_colour_cycle(bulb)
        test_color_temp(bulb)
    finally:
        print("\n[BULB] Test sequence complete. Leaving bulb ON at warm white.")
 
