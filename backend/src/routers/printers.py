from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.printer import Printer, AMS, AMSSlot
from src.schemas.printer import PrinterCreate, PrinterRead, PrinterUpdate, AMSCreate, AMSRead

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("/", response_model=List[PrinterRead])
def get_printers(db: Session = Depends(get_db)):
    return db.query(Printer).all()


@router.get("/{printer_id}", response_model=PrinterRead)
def get_printer(printer_id: int, db: Session = Depends(get_db)):
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    return printer


@router.post("/", response_model=PrinterRead, status_code=201)
def create_printer(printer: PrinterCreate, db: Session = Depends(get_db)):
    db_printer = Printer(**printer.model_dump())
    db.add(db_printer)
    db.commit()
    db.refresh(db_printer)
    return db_printer


@router.patch("/{printer_id}", response_model=PrinterRead)
def update_printer(printer_id: int, printer: PrinterUpdate, db: Session = Depends(get_db)):
    db_printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not db_printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    for key, value in printer.model_dump(exclude_unset=True).items():
        setattr(db_printer, key, value)
    db.commit()
    db.refresh(db_printer)
    return db_printer


@router.delete("/{printer_id}", status_code=204)
def delete_printer(printer_id: int, db: Session = Depends(get_db)):
    db_printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not db_printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    db.delete(db_printer)
    db.commit()


@router.post("/{printer_id}/ams", response_model=AMSRead, status_code=201)
def add_ams(printer_id: int, ams: AMSCreate, db: Session = Depends(get_db)):
    db_printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not db_printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    db_ams = AMS(printer_id=printer_id, **ams.model_dump())
    db.add(db_ams)
    db.commit()
    db.refresh(db_ams)
    # slots automatisch anlegen
    slot_count = 4 if ams.type != "ams_lite" else 4
    for i in range(slot_count):
        db.add(AMSSlot(ams_id=db_ams.id, slot_index=i))
    db.commit()
    db.refresh(db_ams)
    return db_ams


@router.delete("/{printer_id}/ams/{ams_id}", status_code=204)
def delete_ams(printer_id: int, ams_id: int, db: Session = Depends(get_db)):
    db_ams = db.query(AMS).filter(AMS.id == ams_id, AMS.printer_id == printer_id).first()
    if not db_ams:
        raise HTTPException(status_code=404, detail="AMS not found")
    db.delete(db_ams)
    db.commit()
