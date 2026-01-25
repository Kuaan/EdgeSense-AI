#v8.0
import os, json, hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.device_registry import registry
from app.mqtt.client import mqtt_client

router = APIRouter(prefix="/ota", tags=["OTA"])

FIRMWARE_DIR = "firmware"
GATEWAY_HOST = "172.20.10.4"

# ---------- utils ----------
def list_versions():
    return sorted([f.replace(".bin", "") for f in os.listdir(FIRMWARE_DIR) if f.endswith(".bin")])

def latest_version():
    versions = list_versions()
    return versions[-1] if versions else None

def firmware_url(version: str):
    return f"http://{GATEWAY_HOST}:8000/ota/firmware/{version}.bin"

def firmware_md5(version: str):
    path = os.path.join(FIRMWARE_DIR, f"{version}.bin")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest().upper()
    return md5

# ---------- models ----------
class OtaJob(BaseModel):
    uid: str
    version: str | None = None

# ---------- APIs ----------
@router.get("/versions")
def get_versions():
    return {"versions": list_versions(), "latest": latest_version()}

@router.post("/jobs")
def create_job(job: OtaJob):
    job_uid = job.uid.replace(":", "").upper()  # 標準化 UID
    device = registry.devices.get(job_uid)
    if not device:
        raise HTTPException(404, "device not found")

    # ✅ 允許多次 OTA
    if device.status in ["downloading", "flashing", "updating"]:
        raise HTTPException(400, f"device status={device.status} cannot OTA")

    version = job.version or latest_version()
    if not version:
        raise HTTPException(400, "no firmware")

    md5sum = firmware_md5(version)
    if not md5sum:
        raise HTTPException(400, "firmware file not found")

    payload = {
        "version": version,
        "url": firmware_url(version),
        "md5": md5sum
    }

    topic = f"devices/{job_uid}/ota"
    mqtt_client.publish(topic, json.dumps(payload))

    device.status = "downloading"  # 對應 ESP32 OTA Status

    return {"device": job_uid, "version": version, "result": "sent"}

@router.post("/jobs/latest")
def ota_latest(uid: str):
    return create_job(OtaJob(uid=uid))


# ---------- OTA Status 回報用函式 ----------
def handle_ota_status(uid: str, status: str, fw_version: str | None = None):
    uid = uid.replace(":", "").upper()
    device = registry.devices.get(uid)
    if not device:
        return

    device.status = status
    if fw_version and status == "success":
        device.fw_version = fw_version

    # ✅ OTA 完成後自動重置狀態為 online，方便下次 OTA
    if status in ["success", "failed"]:
        device.status = "online"

    print(f"[OTA Status] {uid} → status={status}, fw_version={fw_version}")



'''v5.3
import os, json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.device_registry import registry
from app.mqtt.client import mqtt_client

router = APIRouter(prefix="/ota", tags=["OTA"])

FIRMWARE_DIR = "firmware"


# ---------- utils ----------

def list_versions():
    files = os.listdir(FIRMWARE_DIR)
    return sorted(
        [f.replace(".bin", "") for f in files if f.endswith(".bin")]
    )


def latest_version():
    versions = list_versions()
    if not versions:
        return None
    return versions[-1]


def firmware_url(version: str):
    return f"http://172.20.10.4:8000/ota/firmware/{version}.bin"


# ---------- models ----------

class OtaJob(BaseModel):
    uid: str
    version: str | None = None


# ---------- APIs ----------

@router.get("/versions")
def get_versions():
    return {
        "versions": list_versions(),
        "latest": latest_version()
    }


@router.post("/jobs")
def create_job(job: OtaJob):
    device = registry.devices.get(job.uid)
    if not device:
        raise HTTPException(404, "device not found")

    if device.status != "online":
        raise HTTPException(400, "device offline")

    version = job.version or latest_version()

    if not version:
        raise HTTPException(400, "no firmware")

    payload = {
        "version": version,
        "url": firmware_url(version)
    }

    topic = f"devices/{job.uid}/ota"
    mqtt_client.client.publish(topic, json.dumps(payload))

    device.status = "updating"

    return {
        "device": job.uid,
        "version": version,
        "result": "sent"
    }


@router.post("/jobs/latest")
def ota_latest(uid: str):
    return create_job(OtaJob(uid=uid))
'''

'''v5.2 manual OTA
import json
from fastapi import APIRouter, HTTPException
from app.core.device_registry import registry
from app.mqtt.client import mqtt_client

router = APIRouter(prefix="/ota", tags=["OTA"])

LATEST_VERSION = "v1.1.0"


@router.get("/version")
def get_latest_version():
    return {
        "version": LATEST_VERSION
    }


@router.post("/jobs")
def create_ota_job(device_id: str, version: str):
    device = registry.devices.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.status != "online":
        raise HTTPException(status_code=400, detail="Device not online")

    url = f"http://172.20.10.4:8000/ota/firmware/{version}.bin"
    payload = {
        "url": url
    }

    topic = f"devices/{device_id}/ota"

    print(f"[OTA] publish -> {topic}")
    print(f"[OTA] payload -> {payload}")

    ok = mqtt_client.publish(topic, payload)

    if not ok:
        raise HTTPException(status_code=500, detail="MQTT publish failed")

    device.status = "updating"

    return {
        "result": "sent",
        "device": device_id,
        "version": version,
        "url": url
    }
'''

'''bf v5.2
import json
from fastapi import APIRouter, HTTPException
from app.core.device_registry import registry
from app.mqtt.client import mqtt_client

router = APIRouter(prefix="/ota", tags=["OTA"])

LATEST_VERSION = "v1.1.0"

@router.get("/version")
def get_latest_version():
    return {
        "version": LATEST_VERSION
    }

@router.post("/jobs")
def create_ota_job(device_id: str, version: str):
    device = registry.devices.get(device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    if device.status != "online":
        raise HTTPException(400, "Device not online")

    payload = {
        "version": version,
        "url": f"http://172.20.10.4:8000/ota/firmware/{version}.bin"
    }

    topic = f"devices/{device_id}/ota"
    mqtt_client.client.publish(topic, json.dumps(payload))

    device.status = "updating"

    return {"result": "sent", "device": device_id, "version": version}
'''
