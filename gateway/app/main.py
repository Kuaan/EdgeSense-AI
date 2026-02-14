#v8.5
import asyncio
from fastapi import FastAPI

from app.core.device_registry import registry
from app.services.heartbeat import heartbeat_watcher

from app.mqtt.client import mqtt_client, start
from app.mqtt import handlers

from app.api import devices, ota, firmware
from app.ui.routes import router as ui_router

from fastapi.staticfiles import StaticFiles #

app = FastAPI()
app.include_router(ui_router)
handlers.registry = registry

app.include_router(devices.router)
app.include_router(ota.router)
app.include_router(firmware.router)

app.mount("/firmware", StaticFiles(directory="firmware"), name="firmware") #

@app.on_event("startup")
async def startup_event():
    print("[Gateway] Starting up...")

    start()

    asyncio.create_task(heartbeat_watcher(registry))