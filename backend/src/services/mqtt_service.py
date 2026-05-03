"""
mqtt_service.py – Hält eine persistente MQTT-Verbindung pro Drucker
und cached den letzten bekannten Status.
"""

import ssl
import json
import asyncio
import logging
from typing import Dict, Any, Set, Callable
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class PrinterMQTTClient:
    """Eine persistente MQTT-Verbindung zu einem Bambu-Drucker."""

    def __init__(self, printer_id: int, ip: str, serial: str, access_code: str):
        self.printer_id = printer_id
        self.ip = ip
        self.serial = serial
        self.access_code = access_code

        self.last_status: Dict[str, Any] = {}
        self.is_connected = False

        # Callbacks die bei neuen Daten aufgerufen werden
        self._subscribers: Set[Callable] = set()

        self._client = self._build_client()

    def _build_client(self) -> mqtt.Client:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set("bblp", self.access_code)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        client.tls_set_context(ctx)
        client.tls_insecure_set(True)

        # Auto-Reconnect: nach 5s starten, maximal alle 60s versuchen
        client.reconnect_delay_set(min_delay=5, max_delay=60)

        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message

        return client

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info(f"Drucker {self.printer_id} verbunden")
            client.subscribe(f"device/{self.serial}/report")
            # Einmal alle Daten anfordern
            client.publish(f"device/{self.serial}/request", json.dumps({
                "pushing": {"sequence_id": "0", "command": "pushall", "version": 1, "push_target": 1}
            }))
            # Subscriber über Reconnect/Online informieren
            self._notify_subscribers({**self.last_status, "_online": True})
        else:
            logger.warning(f"Drucker {self.printer_id} Verbindung abgelehnt: {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None, reasoncode=None):
        self.is_connected = False
        logger.info(f"Drucker {self.printer_id} getrennt (rc={rc})")
        # Subscriber sofort über Offline-Status informieren
        self._notify_subscribers({**self.last_status, "_online": False})

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
        except Exception:
            return

        if "print" not in data:
            return

        p = data["print"]

        # push_status UND push_info verarbeiten (Bambu schickt beide)
        if p.get("command") not in ("push_status", "push_info"):
            return

        # Status mergen (Bambu schickt manchmal nur Teilupdates)
        self.last_status.update(p)
        self.last_status["_online"] = True

        self._notify_subscribers(self.last_status)

    def _notify_subscribers(self, status: Dict[str, Any]):
        for callback in self._subscribers.copy():
            try:
                callback(self.printer_id, status)
            except Exception as e:
                logger.error(f"Subscriber Fehler: {e}")

    def subscribe(self, callback: Callable):
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable):
        self._subscribers.discard(callback)

    def connect(self):
        try:
            # connect_async blockiert nicht und arbeitet zusammen mit loop_start
            self._client.connect_async(self.ip, 8883, keepalive=30)
            self._client.loop_start()
        except Exception as e:
            logger.error(f"Drucker {self.printer_id} Verbindungsfehler: {e}")

    def disconnect(self):
        self._client.loop_stop()
        try:
            self._client.disconnect()
        except Exception:
            pass


class MQTTManager:
    """Verwaltet alle Drucker-Verbindungen."""

    def __init__(self):
        self._clients: Dict[int, PrinterMQTTClient] = {}

    def add_printer(self, printer_id: int, ip: str, serial: str, access_code: str):
        if printer_id in self._clients:
            return  # Bereits verbunden

        if not serial:
            logger.warning(f"Drucker {printer_id} hat keine Seriennummer, übersprungen")
            return

        client = PrinterMQTTClient(printer_id, ip, serial, access_code)
        self._clients[printer_id] = client
        client.connect()

    def remove_printer(self, printer_id: int):
        if printer_id in self._clients:
            self._clients[printer_id].disconnect()
            del self._clients[printer_id]

    def get_client(self, printer_id: int) -> PrinterMQTTClient | None:
        return self._clients.get(printer_id)

    def get_status(self, printer_id: int) -> Dict[str, Any]:
        client = self._clients.get(printer_id)
        if not client:
            return {}
        return client.last_status

    def is_connected(self, printer_id: int) -> bool:
        client = self._clients.get(printer_id)
        return client.is_connected if client else False

    def subscribe(self, printer_id: int, callback: Callable):
        client = self._clients.get(printer_id)
        if client:
            client.subscribe(callback)

    def unsubscribe(self, printer_id: int, callback: Callable):
        client = self._clients.get(printer_id)
        if client:
            client.unsubscribe(callback)

    def disconnect_all(self):
        for client in self._clients.values():
            client.disconnect()
        self._clients.clear()


# Singleton
mqtt_manager = MQTTManager()