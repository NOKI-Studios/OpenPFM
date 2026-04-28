from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from src.database import get_db
from src.models.filament import Filament, FilamentSpool
from src.schemas.filament import (
    FilamentCreate, FilamentRead, FilamentUpdate,
    FilamentSpoolCreate, FilamentSpoolRead, FilamentSpoolUpdate
)

router = APIRouter(prefix="/filaments", tags=["filaments"])


@router.get("/", response_model=List[FilamentRead])
def get_filaments(db: Session = Depends(get_db)):
    filaments = db.query(Filament).all()
    result = []
    for f in filaments:
        spool_count = db.query(func.count(FilamentSpool.id)).filter(
            FilamentSpool.filament_id == f.id
        ).scalar()
        filament_read = FilamentRead.model_validate(f)
        filament_read.spool_count = spool_count
        result.append(filament_read)
    return result


@router.get("/{filament_id}", response_model=FilamentRead)
def get_filament(filament_id: int, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    spool_count = db.query(func.count(FilamentSpool.id)).filter(
        FilamentSpool.filament_id == filament_id
    ).scalar()
    result = FilamentRead.model_validate(filament)
    result.spool_count = spool_count
    return result


@router.post("/", response_model=FilamentRead, status_code=201)
def create_filament(filament: FilamentCreate, db: Session = Depends(get_db)):
    db_filament = Filament(**filament.model_dump())
    db.add(db_filament)
    db.commit()
    db.refresh(db_filament)
    return FilamentRead.model_validate(db_filament)


@router.patch("/{filament_id}", response_model=FilamentRead)
def update_filament(filament_id: int, filament: FilamentUpdate, db: Session = Depends(get_db)):
    db_filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not db_filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    for key, value in filament.model_dump(exclude_unset=True).items():
        setattr(db_filament, key, value)
    db.commit()
    db.refresh(db_filament)
    return FilamentRead.model_validate(db_filament)


@router.delete("/{filament_id}", status_code=204)
def delete_filament(filament_id: int, db: Session = Depends(get_db)):
    db_filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not db_filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    db.delete(db_filament)
    db.commit()


# Spool endpoints
@router.get("/{filament_id}/spools", response_model=List[FilamentSpoolRead])
def get_spools(filament_id: int, db: Session = Depends(get_db)):
    return db.query(FilamentSpool).filter(FilamentSpool.filament_id == filament_id).all()


@router.post("/{filament_id}/spools", response_model=FilamentSpoolRead, status_code=201)
def add_spool(filament_id: int, spool: FilamentSpoolCreate, db: Session = Depends(get_db)):
    filament = db.query(Filament).filter(Filament.id == filament_id).first()
    if not filament:
        raise HTTPException(status_code=404, detail="Filament not found")
    db_spool = FilamentSpool(filament_id=filament_id, **spool.model_dump(exclude={"filament_id"}))
    db.add(db_spool)
    db.commit()
    db.refresh(db_spool)
    return db_spool


@router.patch("/spools/{spool_id}", response_model=FilamentSpoolRead)
def update_spool(spool_id: int, spool: FilamentSpoolUpdate, db: Session = Depends(get_db)):
    db_spool = db.query(FilamentSpool).filter(FilamentSpool.id == spool_id).first()
    if not db_spool:
        raise HTTPException(status_code=404, detail="Spool not found")
    for key, value in spool.model_dump(exclude_unset=True).items():
        setattr(db_spool, key, value)
    db.commit()
    db.refresh(db_spool)
    return db_spool


@router.delete("/spools/{spool_id}", status_code=204)
def delete_spool(spool_id: int, db: Session = Depends(get_db)):
    db_spool = db.query(FilamentSpool).filter(FilamentSpool.id == spool_id).first()
    if not db_spool:
        raise HTTPException(status_code=404, detail="Spool not found")
    db.delete(db_spool)
    db.commit()
