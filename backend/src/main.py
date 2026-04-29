from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine, Base
from src.routers import printers, filaments, users, printer_actions
from src.routers import auth
from src.routers.auth import get_current_user

import src.models.printer
import src.models.filament
import src.models.user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpenPFM API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|\d+\.\d+\.\d+\.\d+)(:\d+)?", #TODO: Add Release IP/Domain here
    allow_methods=["*"],
    allow_headers=["*"],
)

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