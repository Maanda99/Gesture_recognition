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


COLOUR_CYCLE = [
    (0, 100),    # red
    (120, 100),  # green
    (240, 100),  # blue
    (280, 80),   # purple
]

