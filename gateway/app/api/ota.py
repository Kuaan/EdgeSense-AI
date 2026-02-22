#v9.0 app/api/ota.py 

import os
import json
import hashlib
import logging
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from app.core.device_registry import registry
from app.core.ota_manager import ota_manager
from app.core.ota_jobs import OTA_JOBS

from app.mqtt.client import mqtt_client
from app.mqtt.handlers import normalize_uid

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ota",
    tags=["OTA"]
)

# =========================================================
# CONFIG
# =========================================================
FIRMWARE_DIR = "firmware"

GATEWAY_HOST = os.getenv(
    "GATEWAY_HOST",
    "172.20.10.4"
)

GATEWAY_PORT = os.getenv(
    "GATEWAY_PORT",
    "8000"
)

# =========================================================
# UTILS
# =========================================================
def list_versions():
    if not os.path.exists(FIRMWARE_DIR):
        return []

    return sorted(
        f for f in os.listdir(FIRMWARE_DIR)
        if f.endswith(".bin")
    )

def get_firmware_path(version):
    candidates = [
        version,
        f"{version}.bin"
    ]
    for c in candidates:
        path = os.path.join(
            FIRMWARE_DIR,
            c
        )

        if os.path.exists(path):
            return c
    return None

def firmware_md5(filename):
    path = os.path.join(
        FIRMWARE_DIR,
        filename
    )
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(
            lambda: f.read(4096),
            b""
        ):
            md5.update(chunk)
    return md5.hexdigest().upper()

# =========================================================
# MODEL
# =========================================================
class OtaJob(BaseModel):
    uid: str
    version: Optional[str] = None
    force: bool = False

# =========================================================
# VERSION LIST
# =========================================================
@router.get("/versions")
def get_versions():
    files = list_versions()
    return {
        "versions":
        [
            f.replace(".bin", "")
            for f in files
        ],
        "latest":
        files[-1].replace(".bin", "")
        if files else None
    }

# =========================================================
# DOWNLOAD
# =========================================================
@router.get("/firmware/{filename}")
def download_firmware(filename: str):
    path = os.path.join(
        FIRMWARE_DIR,
        filename
    )
    if not os.path.exists(path):
        raise HTTPException(
            404,
            "Firmware not found"
        )

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=filename
    )

# =========================================================
# CREATE OTA JOB ⭐
# =========================================================
@router.post("/jobs")
def create_job(job: OtaJob):
    uid = normalize_uid(job.uid)
    device = registry.devices.get(uid)
    if not device:
        raise HTTPException(
            404,
            "device not found"
        )

    # =====================================================
    # create via manager
    # =====================================================
    manager_job = ota_manager.create_job(
        uid,
        job.version,
        force=job.force
    )

    file = get_firmware_path(
        manager_job.version
    )

    if not file:
        raise HTTPException(
            400,
            "firmware not found"
        )

    # =====================================================
    # MQTT
    # =====================================================
    md5 = firmware_md5(file)
    url = (
        f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"
        f"/ota/firmware/{file}"
    )

    payload = {
        "job_id":
        manager_job.job_id,
        "version":
        manager_job.version,
        "url":
        url,
        "md5":
        md5
    }

    topic = f"devices/{uid}/ota"

    mqtt_client.publish(
        topic,
        json.dumps(payload),
        qos=1
    )

    device.status = "downloading"

    logger.info(
        f"[OTA] sent {uid} job={manager_job.job_id}"
    )
    return {
        "job_id":
        manager_job.job_id,
        "uid":
        uid,
        "version":
        manager_job.version,
        "result":
        "sent"
    }

# =========================================================
# RESET
# =========================================================
@router.post("/reset/{uid}")
def reset(uid: str):
    uid = normalize_uid(uid)
    device = registry.devices.get(uid)
    if not device:
        raise HTTPException(
            404,
            "device not found"
        )

    device.status = "online"
    return {
        "result":
        "reset ok"
    }
    
# =========================================================
# LIST JOBS ⭐
# =========================================================
@router.get("/jobs")
def list_jobs():
    return list(
        OTA_JOBS.values()
    )


'''#v8.6 app/api/ota.py 
import os
import json
import hashlib
import logging
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from app.core.ota_jobs import OTA_JOBS
from app.core.device_registry import registry
from app.mqtt.client import mqtt_client
from app.mqtt.handlers import normalize_uid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ota", tags=["OTA"])

# =====================
# Config
# =====================
FIRMWARE_DIR = "firmware"
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "172.20.10.4")
GATEWAY_PORT = os.getenv("GATEWAY_PORT", "8000")

# =====================
# Utils
# =====================
def list_versions():
    if not os.path.exists(FIRMWARE_DIR):
        return []
    return sorted(
        f for f in os.listdir(FIRMWARE_DIR)
        if f.endswith(".bin")
    )

def get_firmware_path(version: str):
    candidates = [
        version,
        f"{version}.bin"
    ]
    for c in candidates:
        path = os.path.join(FIRMWARE_DIR, c)
        if os.path.exists(path):
            return c
    return None

def firmware_md5(filename: str):
    path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(path):
        return None

    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest().upper()

# =====================
# Models
# =====================
class OtaJob(BaseModel):
    uid: str
    version: Optional[str] = None
    job_id: Optional[str] = None
    force: bool = False

# =====================
# APIs
# =====================

# ---------- Firmware List ----------
@router.get("/versions")
def get_versions():
    files = list_versions()
    return {
        "versions":
            [f.replace(".bin", "") for f in files],
        "files": files,
        "latest":
            files[-1].replace(".bin", "")
            if files else None
    }

# ---------- Firmware Download ----------
@router.get("/firmware/{filename}")
def download_firmware(filename: str):
    path = os.path.join(FIRMWARE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Firmware not found")
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=filename
    )

# ---------- Create OTA Job ----------
@router.post("/jobs")
def create_job(job: OtaJob):
    uid = normalize_uid(job.uid)
    device = registry.devices.get(uid)
    if not device:
        raise HTTPException(
            404,
            "device not found"
        )

    if device.status in [
        "downloading",
        "flashing",
        "updating"
    ] and not job.force:
        raise HTTPException(
            400,
            f"device busy status={device.status}"
        )

    # version select
    if job.version:
        file = get_firmware_path(job.version)
    else:
        versions = list_versions()
        file = versions[-1] if versions else None
        
    if not file:
        raise HTTPException(
            400,
            "firmware not found"
        )

    version = file.replace(".bin", "")
    job_id = (
        job.job_id
        or
        f"ota-{int(time.time())}-{uid[-4:]}"
    )

    # ---------- Save Job ----------
    OTA_JOBS[job_id] = {
        "job_id": job_id,
        "uid": uid,
        "version": version,
        "status": "sent",
        "ts": int(time.time())
    }

    # ---------- Prepare MQTT ----------
    md5 = firmware_md5(file)
    url = (
        f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"
        f"/ota/firmware/{file}"
    )

    payload = {
        "job_id": job_id,
        "version": version,
        "url": url,
        "md5": md5
    }

    topic = f"devices/{uid}/ota"
    mqtt_client.publish(
        topic,
        json.dumps(payload),
        qos=1
    )

    device.status = "downloading"
    logger.info(
        f"OTA Job sent to {uid}: {payload}"
    )
    return {
        "job_id": job_id,
        "device": uid,
        "version": version,
        "result": "sent"
    }

# ---------- Emergency Reset ----------
@router.post("/reset/{uid}")
def reset_status(uid: str):
    uid = normalize_uid(uid)
    device = registry.devices.get(uid)
    if not device:
        raise HTTPException(
            404,
            "device not found"
        )

    device.status = "online"
    return {
        "result":
            "device unlocked"
    }
'''

