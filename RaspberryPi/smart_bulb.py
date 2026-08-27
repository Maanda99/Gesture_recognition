import os
import sys
import time

from dotenv import load_dotenv
from PyP100 import PyL530

load_dotenv() # read the .env file in the current working directory

def get_required_env(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        sys.exit(
             f"[CONFIG ERROR] Environment variable {var_name} is not set.\n"
             f"Run: export {var_name}=\"...\" before launching this script."
        )
    return value

def connect_to_bulb() -> PyL530.L530:
    email = get_required_env("MY_EMAIL")
    password = get_required_env("MY_PASSWORD")
    bulb_ip = get_required_env("TAPO_BULB_IP")

    print(f"[BULB] Connecting to {bulb_ip} (protocol auto-negotiated) ...")
    bulb = PyL530.L530(bulb_ip, email, password)

    print("[BULB] Auth OK.")
    return bulb



def test_basic_on_off(bulb: PyL530.L530) -> None:
    print("\n--- Basic on/off test ---")
    info = bulb.getDeviceInfo()
    print(f"[BULB] Device info (nickname/state check): "
          f"on={info.get('device_on')}, model={info.get('model', '?')}")
    
    info = bulb.getDeviceInfo()
    print(info)

    print("[BULB] turn-Off()")
    bulb.turnOff()
    time.sleep(1.5)

    print("[BULB] turn-On()")
    bulb.setColorTemp(2700)
    bulb.turnOn()
    time.sleep(1.5)

    print("[BULB] turn-Off")
    bulb.turnOff()
    time.sleep(1.5)

    print("[BULB] turn-On() again")
    bulb.setColorTemp(2700)
    time.sleep(1)
    bulb.setBrightness(10)
    bulb.turnOn()


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
        time.sleep(1.5)



if __name__ == "__main__":
    bulb = connect_to_bulb()

    try:
        test_basic_on_off(bulb)
        test_colour_cycle(bulb)
    finally:
        print("\n[BULB] Testing complete. Leaving bulb ON")
