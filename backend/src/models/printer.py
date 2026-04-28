from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class PrinterStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    printing = "printing"
    idle = "idle"
    error = "error"


class AMSType(str, enum.Enum):
    ams = "ams"
    ams_lite = "ams_lite"
    ams_hub = "ams_hub"


class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=True)
    ip_address = Column(String, nullable=False)
    access_code = Column(String, nullable=False)
    nozzle_diameter = Column(Float, default=0.4)
    status = Column(Enum(PrinterStatus), default=PrinterStatus.offline)
    has_ams = Column(Boolean, default=False)
    purchase_url = Column(String, nullable=True)

    ams_units = relationship("AMS", back_populates="printer", cascade="all, delete-orphan")


class AMS(Base):
    __tablename__ = "ams_units"

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    ams_index = Column(Integer, nullable=False)
    type = Column(Enum(AMSType), default=AMSType.ams)
    purchase_url = Column(String, nullable=True)

    printer = relationship("Printer", back_populates="ams_units")
    slots = relationship("AMSSlot", back_populates="ams", cascade="all, delete-orphan")


class AMSSlot(Base):
    __tablename__ = "ams_slots"

    id = Column(Integer, primary_key=True, index=True)
    ams_id = Column(Integer, ForeignKey("ams_units.id"), nullable=False)
    slot_index = Column(Integer, nullable=False)
    spool_id = Column(Integer, ForeignKey("filament_spools.id"), nullable=True)

    ams = relationship("AMS", back_populates="slots")
    spool = relationship("FilamentSpool", back_populates="ams_slot")
