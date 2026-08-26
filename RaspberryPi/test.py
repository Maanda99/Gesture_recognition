import requests

ip = "192.168.0.161"
r = requests.post(
    f"http://{ip}/app",
    json={"method": "handshake", "params": {"key": "dummy"}},
    timeout=5,
)
print(r.status_code)
print(r.json())
