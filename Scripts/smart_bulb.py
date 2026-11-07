import os
import sys
import time
import socket
import subprocess

from concurrent.futures import ThreadPoolExecutor
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


def find_bulb_ip(mac: str, retries: int = 3) -> str:
    mac = mac.lower().replace("-", ":")

    # Work out our own subnet (assumes /24, which also covers phone hotspots)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()
    prefix = my_ip.rsplit(".", 1)[0]

    def ping(i):
        try:
            socket.create_connection((f"{prefix}.{i}", 80), timeout=0.5).close()
        except OSError:
            pass


    for attempt in range(1, retries + 1):
        print(f"[BULB] Scanning {prefix}.0/24 for {mac} (attempt {attempt}) ...")
        with ThreadPoolExecutor(max_workers=64) as pool:
            pool.map(ping, range(1, 255))

        out = subprocess.run(["ip", "neigh"], capture_output=True, text=True).stdout
        for line in out.splitlines():
            if mac in line.lower():
                return line.split()[0]
        time.sleep(2)

    raise RuntimeError(f"Could not find a device with MAC {mac} on the network.")


ip_failed_count = 0

def connect_to_bulb() -> PyL530.L530:
    global ip_failed_count
    email = get_required_env("MY_EMAIL")
    password = get_required_env("MY_PASSWORD")
    
    # Priority: Try the .env IP first. Fallback to MAC discovery after 3 failures.
    if ip_failed_count < 3:
        target_ip = get_required_env("TAPO_BULB_IP")
    else:
        print("[BULB] IP failed 3x. Falling back to MAC discovery...")
        target_ip = find_bulb_ip(get_required_env("TAPO_BULB_MAC"))
        ip_failed_count = 0

    print(f"[BULB] Connecting to {target_ip}...")
    try:
        bulb = PyL530.L530(target_ip, email, password)
        bulb.handshake() # Verifies the connection works
        ip_failed_count = 0  # Reset counter on success
        print("[BULB] Auth OK.")
        return bulb
    except Exception as e:
        ip_failed_count += 1
        raise e


COLOUR_CYCLE = [
    (8, 40),
    (0, 100),    # red
    (240, 100),  # blue
]

