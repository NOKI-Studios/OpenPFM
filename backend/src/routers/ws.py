from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
from src.database import SessionLocal
from src.models.printer import Printer
from src.services.mqtt_service import mqtt_manager

router = APIRouter()


@router.websocket("/ws/printers/{printer_id}")
async def printer_ws(websocket: WebSocket, printer_id: int):
    await websocket.accept()

    db: Session = SessionLocal()
    try:
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
    finally:
        db.close()

    if not printer:
        await websocket.close(code=1008)
        return

    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_status_update(pid: int, status: dict):
        # Kopie erstellen, damit spätere Merges den bereits gesendeten Stand nicht verändern
        loop.call_soon_threadsafe(queue.put_nowait, status.copy())

    mqtt_manager.subscribe(printer_id, on_status_update)

    # Sofort den letzten bekannten Status schicken
    current = mqtt_manager.get_status(printer_id)
    if current:
        await websocket.send_json(current)

    try:
        while True:
            try:
                status = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(status)
            except asyncio.TimeoutError:
                # Keepalive damit die Verbindung nicht vom Client getrennt wird
                await websocket.send_json({"ping": True})
    except WebSocketDisconnect:
        pass
    finally:
        mqtt_manager.unsubscribe(printer_id, on_status_update)