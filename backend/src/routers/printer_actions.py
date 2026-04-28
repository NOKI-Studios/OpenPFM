from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

from src.database import get_db
from src.models.printer import Printer
from src.services import printer_service

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
