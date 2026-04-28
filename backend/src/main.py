from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine, Base
from src.routers import printers, filaments, users

# Tabellen erstellen
import src.models.printer
import src.models.filament
import src.models.user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpenPFM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(printers.router)
app.include_router(filaments.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
