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
filename    = sys.argv[4]
ams_slot    = int(sys.argv[5])
plate       = int(sys.argv[6])  if len(sys.argv) > 6  else 1
bed_leveling   = sys.argv[7].lower() == 'true' if len(sys.argv) > 7  else True
timelapse      = sys.argv[8].lower() == 'true' if len(sys.argv) > 8  else False
flow_cali      = sys.argv[9].lower() == 'true' if len(sys.argv) > 9  else False
vibration_cali = sys.argv[10].lower() == 'true' if len(sys.argv) > 10 else False

def _hard_timeout(signum, frame):
    os._exit(1)

if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, _hard_timeout)
    signal.alarm(18)

done = threading.Event()

def on_connect(client, userdata, flags, rc, properties=None):
    if rc != 0:
        done.set()
        return
    client.subscribe(f"device/{serial}/report")
    client.publish(f"device/{serial}/request", json.dumps({
        "print": {
            "sequence_id": "1",
            "command": "project_file",
            "param": f"Metadata/plate_{plate}.gcode",
            "project_id": "0",
            "profile_id": "0",
            "task_id": "0",
            "subtask_id": "0",
            "subtask_name": filename.split("/")[-1],
            "file": "",
            "url": f"file:///{filename}",
            "md5": "",
            "timelapse": timelapse,
            "bed_type": "auto",
            "bed_leveling": bed_leveling,
            "flow_cali": flow_cali,
            "vibration_cali": vibration_cali,
            "layer_inspect": False,
            "use_ams": True,
            "ams_mapping": [ams_slot],
            "plate_idx": plate - 1
        }
    }), qos=1)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except Exception:
        return
    p = data.get("print", {})
    if p.get("command") == "project_file":
        if p.get("result", "").lower() == "success":
            print("Print gestartet")
        else:
            print(f"Fehler: {p.get('reason', 'unbekannt')}")
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
except Exception:
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)
    sys.exit(1)

client.loop_start()
done.wait(timeout=10)
client.disconnect()
client.loop_stop()

if hasattr(signal, 'SIGALRM'):
    signal.alarm(0)

if not done.is_set():
    print("Print gestartet")
