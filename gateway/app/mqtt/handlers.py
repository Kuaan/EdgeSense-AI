#v8.5 app/mqtt/handlers.py
import json
import logging
from app.models.device import Device
from app.core.device_registry import registry
from app.core.ota_jobs import OTA_JOBS

logger = logging.getLogger(__name__)

def normalize_uid(uid: str) -> str:
    """統一 UID 格式：去掉冒號，轉大寫"""
    return uid.replace(":", "").upper()

def on_heartbeat(client, userdata, message):
    """
    Topic: devices/{device_id}/heartbeat
    Payload (optional): {"fw_version":"v0.0.0"}
    """
    try:
        topic = message.topic
        # 安全分割 topic
        parts = topic.split("/")
        if len(parts) < 2: return
        
        uid = normalize_uid(parts[1])

        device = registry.devices.get(uid)
        if not device:
            # 這裡假設你的 Device model 建構子支援這些參數
            device = Device(uid=uid, model="esp32")
            registry.register(device)
            logger.info(f"[Heartbeat] Auto-registered {uid}")

        # 更新 last_seen
        # 假設你的 registry 有這個方法
        if hasattr(registry, 'update_last_seen'):
            registry.update_last_seen(uid)

        # ✅ parse payload（如果有）
        if message.payload:
            try:
                payload_str = message.payload.decode().strip()
                if payload_str:
                    data = json.loads(payload_str)
                    fw_version = data.get("fw_version")
                    if fw_version:
                        device.fw_version = fw_version
            except json.JSONDecodeError:
                pass # 忽略心跳包格式錯誤

        # 這裡為了不洗版，可以註解掉 print
        print(f"[Heartbeat] {uid}, fw_version={device.fw_version}")

    except Exception as e:
        logger.error(f"[Heartbeat Error] {e}")


def on_ota_status(client, userdata, message):
    """
    Paho MQTT callback
    Topic: devices/{device_id}/ota_status
    Payload: JSON {"status": "...", "fw_version": "...", "ts": ...}
    """
    try:
        topic = message.topic
        parts = topic.split("/")
        if len(parts) < 2: return

        uid = normalize_uid(parts[1])
        device = registry.devices.get(uid)
        
        if not device:
            logger.warning(f"[OTA Status] Unknown device {uid}")
            return

        payload_str = message.payload.decode().strip()
        if not payload_str: return

        data = json.loads(payload_str)
        status = data.get("status")
        fw_version = data.get("fw_version")
        job_id = data.get("job_id")


        if status:
            device.status = status  # downloading / flashing / success / failed

        if fw_version and status == "success":
            device.fw_version = fw_version
        
        if job_id and job_id in OTA_JOBS:
            OTA_JOBS[job_id]["status"] = status
            OTA_JOBS[job_id]["updated_at"] = data.get("ts")

        logger.info(f"[OTA Status] {uid} -> status={device.status}, fw_version={device.fw_version}")

    except Exception as e:
        logger.error(f"[OTA Status Error] {e}")