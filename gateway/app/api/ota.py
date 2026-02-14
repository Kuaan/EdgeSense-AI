#v8.5 
import os
import json
import hashlib
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import time
from uuid import uuid4
from app.core.ota_jobs import OTA_JOBS

from app.core.device_registry import registry
from app.mqtt.client import mqtt_client
# 引入你在 handlers 定義的正規化函式，確保邏輯一致
from app.mqtt.handlers import normalize_uid 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ota", tags=["OTA"])

FIRMWARE_DIR = "firmware"
#GATEWAY_HOST = os.getenv("GATEWAY_HOST", "192.168.1.20")
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "172.20.10.4")
GATEWAY_PORT = os.getenv("GATEWAY_PORT", "8000")



# ---------- Utils ----------
def list_versions():
    if not os.path.exists(FIRMWARE_DIR): return []
    return sorted([f for f in os.listdir(FIRMWARE_DIR) if f.endswith(".bin")])

def get_firmware_path(version_str: str) -> Optional[str]:
    """處理有無 .bin 的檔名"""
    candidates = [version_str, f"{version_str}.bin"]
    for c in candidates:
        path = os.path.join(FIRMWARE_DIR, c)
        if os.path.exists(path):
            return c
    return None

def firmware_md5(filename: str):
    path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(path): return None
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest().upper()

# ---------- Models ----------
class OtaJob(BaseModel):
    uid: str
    version: str | None = None
    ###
    job_id: Optional[str] = None
    force: bool = False

# ---------- APIs ----------
@router.get("/versions")
def get_versions():
    """獲取可用韌體列表與最新版本"""
    v_files = list_versions()
    return {
        "versions": [v.replace(".bin", "") for v in v_files], 
        "latest": v_files[-1].replace(".bin", "") if v_files else None,
        "files": v_files
    }
    
@router.get("/firmware/{filename}")
def download_firmware(filename: str):
    """設備下載韌體的接口"""
    file_path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(404, "Firmware not found")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)

@router.post("/jobs")
def create_job(job: OtaJob):
    uid = normalize_uid(job.uid)
    device = registry.devices.get(uid)

    if not device:
        raise HTTPException(404, "device not found")

    if device.status in ["downloading", "flashing", "updating"] and not job.force:
        raise HTTPException(400, f"device status={device.status} cannot OTA")

    # 版本選擇
    if job.version:
        target_file = get_firmware_path(job.version)
    else:
        versions = list_versions()
        target_file = versions[-1] if versions else None

    if not target_file:
        raise HTTPException(400, "firmware file not found")

    job_id = job.job_id or f"ota-{int(time.time())}-{uid[-4:]}"

    OTA_JOBS[job_id] = {
        "job_id": job_id,
        "uid": uid,
        "version": target_file.replace(".bin", ""),
        "status": "sent",
        "created_at": time.time()
    }

    md5sum = firmware_md5(target_file)
    url = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/ota/firmware/{target_file}"

    payload = {
        "job_id": job_id,
        "version": target_file.replace(".bin", ""),
        "url": url,
        "md5": md5sum
    }

    topic = f"devices/{uid}/ota"
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

    device.status = "downloading"
    logger.info(f"OTA Job sent to {uid}: {payload}")

    return {"job_id": job_id, "device": uid, "version": target_file, "result": "sent"}

    # 使用與 handler 一致的 UID 處理方式
    uid = normalize_uid(job.uid)
    device = registry.devices.get(uid)
    job_id = job.job_id or f"ota-{int(time.time())}-{uid[-4:]}"
    OTA_JOBS[job_id] = {
    "job_id": job_id,
    "uid": uid,
    "version": target_file.replace(".bin", ""),
    "status": "sent",
    "created_at": time.time()
    }
    
    if not device:
        raise HTTPException(404, "device not found")

    # 因為有了 handlers.on_ota_status，設備回報 success 後，
    # status 就不再是 "downloading"，所以這裡就能通過了。
    if device.status in ["downloading", "flashing", "updating"]:
        raise HTTPException(400, f"device status={device.status} cannot OTA")

    # 版本選擇
    if job.version:
        target_file = get_firmware_path(job.version)
    else:
        versions = list_versions()
        target_file = versions[-1] if versions else None

    if not target_file:
        raise HTTPException(400, "firmware file not found")

    md5sum = firmware_md5(target_file)
    url = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/ota/firmware/{target_file}"

    payload = {
        "job_id": job_id, 
        "version": target_file.replace(".bin", ""),
        "url": url,
        "md5": md5sum
    }

    topic = f"devices/{uid}/ota"
    mqtt_client.publish(topic, json.dumps(payload), qos=1)

    # 鎖定狀態
    device.status = "downloading"
    logger.info(f"OTA Job sent to {uid}: {payload}")

    return {"device": uid, "version": target_file, "result": "sent"}

@router.post("/reset/{uid}")
def reset_status(uid: str):
    """[救急用] 手動解鎖卡住的狀態"""
    uid = normalize_uid(uid)
    device = registry.devices.get(uid)
    if device:
        device.status = "online"
        return {"msg": "Status reset to online"}
    return {"msg": "Device not found"}