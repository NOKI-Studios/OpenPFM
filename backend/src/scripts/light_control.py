import sys
import json
import os
import signal
sys.path.insert(0, os.path.dirname(__file__))
from bambu_mqtt import run

ip          = sys.argv[1]
serial      = sys.argv[2]
access_code = sys.argv[3]
mode        = sys.argv[4] if len(sys.argv) > 4 else "on"  # on, off, flashing

def on_connect(client, serial):
    client.publish(f"device/{serial}/request", json.dumps({
        "system": {
            "sequence_id": "1",
            "command": "ledctrl",
            "led_node": "work_light",
            "led_mode": mode,
            "led_on_time": 500,
            "led_off_time": 500,
            "loop_times": 0,
            "interval_time": 0
        }
    }), qos=1)

def on_message(data):
    s = data.get("system", {})
    if s.get("command") == "ledctrl":
        print(f"Licht: {mode}")
        return True
    return None

result = run(ip, access_code, serial, on_connect, on_message, reply_timeout=6)
if result is None:
    print(f"Licht: {mode}")
