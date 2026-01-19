from fastapi import FastAPI 
from app.api import devices, system

app = FastAPI(
    title="Edge AI Gateway",
    version="0.1.0",
)

app.include_router(devices.router, prefix="/api/devices")
app.include_router(system.router, prefix="/api/system")
