"""
src/routers/snapshot.py

GET /printers/{printer_id}/snapshot

Ablauf für Bambu A1/P1 (Firmware 01.04+):
  1. Kamera per MQTT starten  (ipcam_record_set → enable)
  2. Kurz warten bis der Stream auf Port 6000 bereit ist
  3. TLS-Verbindung zu Port 6000, Auth-Paket schicken, JPEG-Frame lesen
  4. Kamera per MQTT stoppen  (ipcam_record_set → disable)

Port-6000-Protokoll (reverse engineered, Quelle: mattcar15/bambu-connect):
  80-Byte Auth-Paket: 0x40 | 0x3000 | 0x00 | 0x00 | "bblp" (32B) | access_code (32B)
  Danach streamt der Drucker JPEG-Frames (SOI: FF D8 FF E0, EOI: FF D9).
"""

import asyncio
import json
import ssl
import struct
import socket
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.printer import Printer
from src.services.mqtt_service import mqtt_manager

router = APIRouter(prefix="/printers", tags=["snapshot"])

CAMERA_PORT      = 6000
TIMEOUT          = 15   # Sekunden für Socket
CAMERA_START_WAIT = 4   # Sekunden warten nach MQTT-Start
CHUNK_SIZE       = 4096

JPEG_START = bytes([0xFF, 0xD8, 0xFF, 0xE0])
JPEG_END   = bytes([0xFF, 0xD9])


# ── MQTT Camera Start/Stop ────────────────────────────────────────────────────

def _mqtt_camera(printer_id: int, enable: bool):
    client = mqtt_manager.get_client(printer_id)
    if not client or not client.is_connected:
        return
    payload = json.dumps({
        "camera": {
            "sequence_id": "0",
            "command": "ipcam_record_set",
            "control": "enable" if enable else "disable",
        }
    })
    client._client.publish(f"device/{client.serial}/request", payload)


# ── Port-6000 JPEG-Frame ──────────────────────────────────────────────────────

def _build_auth_packet(access_code: str) -> bytes:
    username = "bblp"
    data = bytearray()
    data += struct.pack("<I", 0x40)
    data += struct.pack("<I", 0x3000)
    data += struct.pack("<I", 0)
    data += struct.pack("<I", 0)
    data += username.encode("ascii").ljust(32, b"\x00")
    data += access_code.encode("ascii").ljust(32, b"\x00")
    return bytes(data)


def _find_jpeg(buf: bytearray):
    start = buf.find(JPEG_START)
    if start == -1:
        return None, buf
    end = buf.find(JPEG_END, start + len(JPEG_START))
    if end == -1:
        return None, buf
    end += len(JPEG_END)
    return bytes(buf[start:end]), bytearray(buf[end:])


def _capture_frame_sync(ip: str, access_code: str) -> bytes:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    auth_packet = _build_auth_packet(access_code)

    with socket.create_connection((ip, CAMERA_PORT), timeout=TIMEOUT) as sock:
        with ctx.wrap_socket(sock, server_hostname=ip) as ssock:
            ssock.write(auth_packet)
            buf = bytearray()
            while True:
                chunk = ssock.recv(CHUNK_SIZE)
                if not chunk:
                    break
                buf += chunk
                img, buf = _find_jpeg(buf)
                if img:
                    return img

    raise RuntimeError("Kein JPEG-Frame empfangen")


async def _capture_frame(ip: str, access_code: str) -> bytes:
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _capture_frame_sync, ip, access_code),
            timeout=TIMEOUT + 1,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Kamera-Timeout")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kamera-Fehler: {e}")


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.get("/{printer_id}/snapshot", response_class=Response)
async def get_snapshot(printer_id: int, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    if not printer.ip_address or not printer.access_code:
        raise HTTPException(status_code=400, detail="IP oder Access-Code fehlt")

    # Kamera starten und Stream aufwärmen lassen
    _mqtt_camera(printer_id, enable=True)
    await asyncio.sleep(CAMERA_START_WAIT)

    try:
        jpeg_bytes = await _capture_frame(printer.ip_address, printer.access_code)
    finally:
        _mqtt_camera(printer_id, enable=False)

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Access-Control-Allow-Origin": "*",
        },
    )