#v10.0
import asyncio


from fastapi import FastAPI


from app.core.device_registry import registry
from app.services.heartbeat import heartbeat_watcher

from app.mqtt.client import mqtt_client, start
from app.mqtt import handlers

from app.api import devices, ota, firmware, events
from app.ui.routes import router as ui_router

from fastapi.staticfiles import StaticFiles #

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

handlers.registry = registry

app = FastAPI()
app.include_router(ui_router)
app.include_router(devices.router)
app.include_router(ota.router)
app.include_router(firmware.router)
app.include_router(events.router)

app.mount("/firmware", StaticFiles(directory="firmware"), name="firmware") #

@app.on_event("startup")
async def startup_event():
    print("[Gateway] Starting up...")

    start()

    asyncio.create_task(heartbeat_watcher(registry))


'''bf v5.4
import asyncio
from fastapi import FastAPI

from app.core.device_registry import registry
from app.services.heartbeat import heartbeat_watcher

from app.mqtt.client import mqtt_client
from app.mqtt import handlers

from app.api import devices, ota, firmware

app = FastAPI()

# ✅ 注入 registry 給 MQTT
handlers.registry = registry

# ✅ 掛 router
app.include_router(devices.router)
app.include_router(ota.router)
app.include_router(firmware.router)


@app.on_event("startup")
async def startup_event():
    print("[Gateway] Starting up...")

    mqtt_client.start()
    asyncio.create_task(heartbeat_watcher(registry))
'''    

