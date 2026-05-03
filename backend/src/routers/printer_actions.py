from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import asyncio
import json
import ssl
import struct
import socket

from src.database import get_db
from src.models.printer import Printer
from src.services import printer_service
from src.services.mqtt_service import mqtt_manager

router = APIRouter(prefix="/printers", tags=["printer-actions"])


def get_printer_or_404(printer_id: int, db: Session) -> Printer:
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    if not printer.serial_number:
        raise HTTPException(status_code=400, detail="Printer has no serial number configured")
    return printer


@router.get("/{printer_id}/status")
def get_status(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    status = printer_service.get_status(printer.ip_address, printer.serial_number, printer.access_code)
    if status is None:
        raise HTTPException(status_code=503, detail="Could not reach printer")
    return status


@router.post("/{printer_id}/stop")
def stop_print(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.stop_print(printer.ip_address, printer.serial_number, printer.access_code)


@router.post("/{printer_id}/home")
def home_printer(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.home_printer(printer.ip_address, printer.serial_number, printer.access_code)


@router.post("/{printer_id}/clear-error")
def clear_error(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.clear_error(printer.ip_address, printer.serial_number, printer.access_code)


@router.get("/{printer_id}/files")
def list_files(printer_id: int, path: str = "/", db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.list_files(printer.ip_address, printer.access_code, path)


@router.delete("/{printer_id}/files")
def delete_file(printer_id: int, remote_path: str, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.delete_file(printer.ip_address, printer.access_code, remote_path)


class StartPrintRequest(BaseModel):
    filename: str
    ams_slot: int = 0
    plate: int = 1
    bed_leveling: bool = True
    timelapse: bool = False
    flow_cali: bool = False
    vibration_cali: bool = False


@router.post("/{printer_id}/print")
def start_print(printer_id: int, body: StartPrintRequest, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.start_print(
        printer.ip_address,
        printer.serial_number,
        printer.access_code,
        body.filename,
        body.ams_slot,
        body.plate,
        body.bed_leveling,
        body.timelapse,
        body.flow_cali,
        body.vibration_cali,
    )


@router.post("/{printer_id}/upload")
async def upload_file(
    printer_id: int,
    remote_path: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    printer = get_printer_or_404(printer_id, db)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = printer_service.upload_file(printer.ip_address, printer.access_code, tmp_path, remote_path)
    finally:
        os.unlink(tmp_path)
    return result


class LightRequest(BaseModel):
    mode: str = "on"  # on, off, flashing


@router.post("/{printer_id}/light")
def control_light(printer_id: int, body: LightRequest, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.control_light(
        printer.ip_address, printer.serial_number, printer.access_code, body.mode
    )


@router.post("/{printer_id}/pause")
def pause_print(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.pause_print(
        printer.ip_address, printer.serial_number, printer.access_code
    )


@router.post("/{printer_id}/resume")
def resume_print(printer_id: int, db: Session = Depends(get_db)):
    printer = get_printer_or_404(printer_id, db)
    return printer_service.resume_print(
        printer.ip_address, printer.serial_number, printer.access_code
    )


# ── Snapshot ──────────────────────────────────────────────────────────────────
#
# GET /printers/{printer_id}/snapshot
#
# Flow for Bambu A1/P1 (Firmware 01.04+):
#   1. Start camera via MQTT  (ipcam_record_set → enable)
#   2. Wait briefly for the stream on port 6000 to be ready
#   3. TLS connection to port 6000, send auth packet, read JPEG frame
#   4. Stop camera via MQTT   (ipcam_record_set → disable)
#
# Port-6000 protocol (reverse engineered, source: mattcar15/bambu-connect):
#   80-byte auth packet: 0x40 | 0x3000 | 0x00 | 0x00 | "bblp" (32B) | access_code (32B)
#   The printer then streams JPEG frames (SOI: FF D8 FF E0, EOI: FF D9).

CAMERA_PORT       = 6000
TIMEOUT           = 15   # seconds for socket
CAMERA_START_WAIT = 4    # seconds to wait after MQTT start
CHUNK_SIZE        = 4096

JPEG_START = bytes([0xFF, 0xD8, 0xFF, 0xE0])
JPEG_END   = bytes([0xFF, 0xD9])


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

    raise RuntimeError("No JPEG frame received")


async def _capture_frame(ip: str, access_code: str) -> bytes:
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _capture_frame_sync, ip, access_code),
            timeout=TIMEOUT + 1,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Camera timeout")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Camera error: {e}")


@router.get("/{printer_id}/snapshot", response_class=Response)
async def get_snapshot(printer_id: int, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    if not printer.ip_address or not printer.access_code:
        raise HTTPException(status_code=400, detail="IP or access code missing")

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