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
