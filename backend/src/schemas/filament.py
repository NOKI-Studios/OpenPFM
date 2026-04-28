from pydantic import BaseModel
from typing import Optional
from src.models.filament import FilamentMaterial, SpoolLocation


class FilamentBase(BaseModel):
    name: str
    brand: str
    material: FilamentMaterial
    color: str
    color_hex: Optional[str] = None
    nozzle_temp_min: int
    nozzle_temp_max: int
    bed_temp: int
    spool_weight_total: float = 1000.0
    purchase_url: Optional[str] = None
    low_stock_threshold: int = 1


class FilamentCreate(FilamentBase):
    pass


class FilamentUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    material: Optional[FilamentMaterial] = None
    color: Optional[str] = None
    color_hex: Optional[str] = None
    nozzle_temp_min: Optional[int] = None
    nozzle_temp_max: Optional[int] = None
    bed_temp: Optional[int] = None
    spool_weight_total: Optional[float] = None
    purchase_url: Optional[str] = None
    low_stock_threshold: Optional[int] = None


class FilamentRead(FilamentBase):
    id: int
    spool_count: int = 0

    class Config:
        from_attributes = True


class FilamentSpoolBase(BaseModel):
    filament_id: int
    weight_remaining: float
    location: SpoolLocation = SpoolLocation.warehouse
    printer_id: Optional[int] = None
    notes: Optional[str] = None


class FilamentSpoolCreate(FilamentSpoolBase):
    pass


class FilamentSpoolUpdate(BaseModel):
    weight_remaining: Optional[float] = None
    location: Optional[SpoolLocation] = None
    printer_id: Optional[int] = None
    notes: Optional[str] = None


class FilamentSpoolRead(FilamentSpoolBase):
    id: int

    class Config:
        from_attributes = True
