"""
bambu_mqtt.py – gemeinsame MQTT-Basisklasse für alle Bambu-Scripts.

Strategie:
- Verbindung mit hartem Timeout via signal.alarm (SIGALRM, Linux only)
- loop_start() statt loop_forever() → kein blockierender Thread
- Nach Empfang der gesuchten Antwort sofort disconnect + sys.exit
- Falls kein Signal empfangen: Timeout beendet den Prozess hart
"""

import ssl
import json
import sys
import os
import signal
import threading
import paho.mqtt.client as mqtt

CONNECT_TIMEOUT = 8   # Sekunden bis Verbindung steht
REPLY_TIMEOUT   = 8   # Sekunden bis Antwort kommt
TOTAL_TIMEOUT   = 18  # Harter Gesamttimeout – danach SIGKILL-äquivalent


def _hard_timeout(signum, frame):
    """SIGALRM Handler – beendet den Prozess hart wenn alles andere hängt."""
    sys.stderr.write("TIMEOUT: Script wurde nach hartem Timeout beendet\n")
    os._exit(1)


def make_client(ip, access_code):
    """Erstellt und konfiguriert einen MQTT-Client."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set("bblp", access_code)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    client.tls_set_context(ctx)
    client.tls_insecure_set(True)
    return client


def run(ip, access_code, serial,
        on_connect_cb,
        on_message_cb=None,
        reply_timeout=REPLY_TIMEOUT):
    """
    Verbindet, ruft on_connect_cb auf, wartet auf on_message_cb-Ergebnis.
    on_connect_cb(client, serial) → wird nach erfolgreicher Verbindung aufgerufen.
    on_message_cb(data) → soll True zurückgeben wenn fertig, None/False zum Weiterwarten.
    """

    # Harter Gesamttimeout – schützt vor allem
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, _hard_timeout)
        signal.alarm(TOTAL_TIMEOUT)

    done = threading.Event()
    result = {'value': None}

    def _on_connect(client, userdata, flags, rc, properties=None):
        if rc != 0:
            sys.stderr.write(f"Verbindung abgelehnt, Code: {rc}\n")
            done.set()
            return
        client.subscribe(f"device/{serial}/report")
        on_connect_cb(client, serial)

    def _on_message(client, userdata, msg):
        if on_message_cb is None:
            return
        try:
            data = json.loads(msg.payload.decode())
        except Exception:
            return
        res = on_message_cb(data)
        if res is not None:
            result['value'] = res
            done.set()

    def _on_disconnect(client, userdata, rc, properties=None, reasoncode=None):
        done.set()

    client = make_client(ip, access_code)
    client.on_connect    = _on_connect
    client.on_message    = _on_message
    client.on_disconnect = _on_disconnect

    try:
        client.connect(ip, 8883, keepalive=10)
    except Exception as e:
        sys.stderr.write(f"Verbindung fehlgeschlagen: {e}\n")
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        return None

    client.loop_start()
    done.wait(timeout=reply_timeout)
    client.loop_stop(force=True)

    try:
        client.disconnect()
    except Exception:
        pass

    # Alarm deaktivieren
    if hasattr(signal, 'SIGALRM'):
        signal.alarm(0)

    return result['value']
