from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import enum

from src.database import Base


class FilamentMaterial(str, enum.Enum):
    pla = "PLA"
    petg = "PETG"
    abs = "ABS"
    asa = "ASA"
    tpu = "TPU"
    pa = "PA"
    pc = "PC"
    pla_cf = "PLA-CF"
    petg_cf = "PETG-CF"
    other = "Other"


class SpoolLocation(str, enum.Enum):
    warehouse = "warehouse"
    ams = "ams"
    printer = "printer"


class Filament(Base):
    __tablename__ = "filaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    material = Column(Enum(FilamentMaterial), nullable=False)
    color = Column(String, nullable=False)
    color_hex = Column(String, nullable=True)
    nozzle_temp_min = Column(Integer, nullable=False)
    nozzle_temp_max = Column(Integer, nullable=False)
    bed_temp = Column(Integer, nullable=False)
    spool_weight_total = Column(Float, default=1000.0)
    purchase_url = Column(String, nullable=True)
    low_stock_threshold = Column(Integer, default=1)

    spools = relationship("FilamentSpool", back_populates="filament")


class FilamentSpool(Base):
    __tablename__ = "filament_spools"

    id = Column(Integer, primary_key=True, index=True)
    filament_id = Column(Integer, ForeignKey("filaments.id"), nullable=False)
    weight_remaining = Column(Float, nullable=False)
    location = Column(Enum(SpoolLocation), default=SpoolLocation.warehouse)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=True)
    notes = Column(String, nullable=True)

    filament = relationship("Filament", back_populates="spools")
    ams_slot = relationship("AMSSlot", back_populates="spool", uselist=False)
    printer = relationship("Printer")
