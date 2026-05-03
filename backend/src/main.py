from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from src.services.mqtt_service import mqtt_manager
from src.database import engine, Base, SessionLocal
from src.models.printer import Printer
from src.routers import printers, filaments, users, printer_actions
from src.routers import auth, ws
from src.routers.auth import get_current_user

import src.models.printer
import src.models.filament
import src.models.user

logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect all printers from DB
    db = SessionLocal()
    try:
        printers_list = db.query(Printer).all()
        for p in printers_list:
            if p.serial_number:
                mqtt_manager.add_printer(p.id, p.ip_address, p.serial_number, p.access_code)
        logger.info(f"{len(printers_list)} printers loaded")
    finally:
        db.close()

    yield  # App running

    # Shutdown
    mqtt_manager.disconnect_all()

app = FastAPI(title="OpenPFM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|\d+\.\d+\.\d+\.\d+)(:\d+)?",  # TODO: Add Release IP/Domain here
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws.router)
app.include_router(auth.router)

app.include_router(printers.router, dependencies=[Depends(get_current_user)])
app.include_router(filaments.router, dependencies=[Depends(get_current_user)])
app.include_router(users.router, dependencies=[Depends(get_current_user)])
app.include_router(printer_actions.router, dependencies=[Depends(get_current_user)])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)