from pydantic import BaseModel
from typing import Optional, List
from src.models.printer import PrinterStatus, AMSType


class AMSSlotBase(BaseModel):
    slot_index: int
    spool_id: Optional[int] = None


class AMSSlotCreate(AMSSlotBase):
    pass


class AMSSlotRead(AMSSlotBase):
    id: int
    ams_id: int

    class Config:
        from_attributes = True


class AMSBase(BaseModel):
    ams_index: int
    type: AMSType = AMSType.ams
    purchase_url: Optional[str] = None


class AMSCreate(AMSBase):
    pass


class AMSRead(AMSBase):
    id: int
    printer_id: int
    slots: List[AMSSlotRead] = []

    class Config:
        from_attributes = True


class PrinterBase(BaseModel):
    name: str
    model: str
    serial_number: Optional[str] = None
    ip_address: str
    access_code: str
    nozzle_diameter: float = 0.4
    has_ams: bool = False
    purchase_url: Optional[str] = None


class PrinterCreate(PrinterBase):
    pass


class PrinterUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    ip_address: Optional[str] = None
    access_code: Optional[str] = None
    nozzle_diameter: Optional[float] = None
    has_ams: Optional[bool] = None
    purchase_url: Optional[str] = None
    status: Optional[PrinterStatus] = None


class PrinterRead(PrinterBase):
    id: int
    status: PrinterStatus
    ams_units: List[AMSRead] = []

    class Config:
        from_attributes = True
