import sys
import json
import threading
import signal
import os
import ssl
import paho.mqtt.client as mqtt

ip          = sys.argv[1]
serial      = sys.argv[2]
access_code = sys.argv[3]

def _hard_timeout(signum, frame):
    os._exit(1)

if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, _hard_timeout)
    signal.alarm(18)

merged = {}
done   = threading.Event()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        done.set()
        return
    client.subscribe(f"device/{serial}/report")
    client.publish(f"device/{serial}/request", json.dumps({
        "pushing": {
            "sequence_id": "0",
            "command": "pushall",
            "version": 1,
            "push_target": 1
        }
    }))

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except Exception:
        return
    if 'print' not in data:
        return
    p = data['print']
    if p.get('command') != 'push_status':
        return
    merged.update(p)
    if p.get('msg') == 0 or 'gcode_state' in merged:
        done.set()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set("bblp", access_code)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
client.tls_set_context(ctx)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(ip, 8883, keepalive=10)
except Exception as e:
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)
    print("null")
    sys.exit(1)

client.loop_start()
done.wait(timeout=10)
client.disconnect()
client.loop_stop()

if hasattr(signal, 'SIGALRM'):
    signal.alarm(0)

print(json.dumps(merged if merged else None))
