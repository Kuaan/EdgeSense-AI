#v1.1.1 app/main.py
import asyncio
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# core
from app.core.device_registry import registry
from app.services.heartbeat import heartbeat_watcher
from app.mqtt.client import mqtt_client, start as start_mqtt
from app.mqtt import handlers
from app.api import devices, ota, firmware, events
from app.ui.routes import router as ui_router

# setting Log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# registry->handlers
handlers.registry = registry


# (EdgeSense-AI/)
BASE_DIR = Path(__file__).resolve().parent.parent
#  /home/pi/gateway/firmware
FIRMWARE_DIR = Path("/home/pi/gateway/firmware")
STATIC_DIR = BASE_DIR / "static"
CAPTURES_DIR = STATIC_DIR / "captures"

for d in [FIRMWARE_DIR, STATIC_DIR, CAPTURES_DIR]:
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {d}")

# --- 1. 定義 Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("EdgeSense-AI Gateway 啟動中...")
    
    try:
        start_mqtt() 
    except Exception as e:
        print(f"⚠️ MQTT 啟動失敗 (可能是沒開 Broker): {e}")
    
    asyncio.create_task(heartbeat_watcher(registry)) 
    
    yield
    print("🛑 Gateway 安全關閉中...")

# --- 2. FastAPI  ---
app = FastAPI(lifespan=lifespan, title="EdgeSense-AI Gateway")

# --- 3. router ---
app.include_router(ui_router)
app.include_router(devices.router)
app.include_router(ota.router)
app.include_router(firmware.router)
app.include_router(events.router)

# --- 4. mount static files ---
app.mount("/firmware", StaticFiles(directory=str(FIRMWARE_DIR)), name="firmware")

# web
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

