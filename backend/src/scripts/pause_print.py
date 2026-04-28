import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from bambu_mqtt import run

ip          = sys.argv[1]
serial      = sys.argv[2]
access_code = sys.argv[3]

def on_connect(client, serial):
    client.publish(f"device/{serial}/request", json.dumps({
        "print": {
            "sequence_id": "1",
            "command": "pause"
        }
    }), qos=1)

def on_message(data):
    p = data.get("print", {})
    if p.get("command") == "pause":
        if p.get("result", "").lower() == "success":
            print("Druck pausiert")
        else:
            print(f"Fehler: {p.get('reason', 'unbekannt')}")
        return True
    return None

result = run(ip, access_code, serial, on_connect, on_message, reply_timeout=8)
if result is None:
    print("Druck pausiert")
