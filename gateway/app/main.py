#v8.0(v5.4)
import asyncio
from fastapi import FastAPI

from app.core.device_registry import registry
from app.services.heartbeat import heartbeat_watcher

from app.mqtt.client import mqtt_client, start
from app.mqtt import handlers

from app.api import devices, ota, firmware

app = FastAPI()

handlers.registry = registry

app.include_router(devices.router)
app.include_router(ota.router)
app.include_router(firmware.router)


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

