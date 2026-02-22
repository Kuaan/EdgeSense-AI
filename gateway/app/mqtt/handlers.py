# v10.0 app/mqtt/handlers.py

import json
import logging
import time

from app.models.device import Device
from app.core.device_registry import registry
from app.core.ota_jobs import OTA_JOBS
from app.core.event_manager import event_manager

logger = logging.getLogger(__name__)
# =========================================================
# UID normalize
# =========================================================
def normalize_uid(uid: str) -> str:
    """統一 UID 格式：去掉冒號，轉大寫"""
    return uid.replace(":", "").upper()

# =========================================================
# Heartbeat
# =========================================================
def on_heartbeat(client, userdata, message):
    try:
        parts = message.topic.split("/")
        if len(parts) < 2:
            return
        uid = normalize_uid(parts[1])
        device = registry.devices.get(uid)
        # auto register
        if not device:
            device = Device(
                uid=uid,
                model="esp32"
            )
            registry.register(device)
            logger.info(f"[Heartbeat] Auto-registered {uid}")

        # update last seen
        if hasattr(registry, "update_last_seen"):
            registry.update_last_seen(uid)
        else:
            device.last_seen = time.time()
            
        # parse payload
        if message.payload:
            try:
                data = json.loads(
                    message.payload.decode().strip()
                )
                fw_version = data.get("fw_version")
                if fw_version:
                    device.fw_version = fw_version
                #    
                print(f"[Heartbeat] {uid}, fw_version={device.fw_version}")
                #
            except Exception as e: 
                logger.warning(f"Payload parse error: {e}")
        
        logger.info(
            f"[Heartbeat] {uid}, fw={device.fw_version}"
        )

    except Exception as e:
        logger.error(f"[Heartbeat Error] {e}")


# =========================================================
# OTA STATUS  ⭐ 工業級版本
# =========================================================
def on_ota_status(client, userdata, message):
    try:
        parts = message.topic.split("/")
        if len(parts) < 2:
            return

        uid = normalize_uid(parts[1])
        device = registry.devices.get(uid)

        if not device:
            logger.warning(
                f"[OTA] unknown device {uid}"
            )
            return

        payload_str = message.payload.decode().strip()
        if not payload_str:
            return

        data = json.loads(payload_str)
        status = data.get("status")
        fw_version = data.get("fw_version")
        job_id = data.get("job_id")
        ts = data.get("ts", time.time())
        
        # =====================================================
        # update device state
        # =====================================================
        if status:
            device.status = status

        if status == "success":
            device.status = "online"
            if fw_version:
                device.fw_version = fw_version

        if status == "failed":
            device.status = "online"

        # =====================================================
        # update OTA JOB
        # =====================================================
        if job_id and job_id in OTA_JOBS:
            job = OTA_JOBS[job_id]
            job["status"] = status
            job["updated_at"] = ts

            if status == "success":
                job["completed_at"] = ts
                job["result"] = "success"

            elif status == "failed":
                job["completed_at"] = ts
                job["result"] = "failed"

        else:
            logger.warning(
                f"[OTA] job not found {job_id}"
            )

        logger.info(
            f"[OTA] {uid} job={job_id} status={status}"
        )

    except Exception as e:
        logger.error(
            f"[OTA Status Error] {e}"
        )

# =========================================================
# EVENT
# =========================================================
def on_event(client, userdata, message):
    try:
        parts = message.topic.split("/")
        if len(parts) < 2:
            return
        uid = normalize_uid(parts[1])
        payload_str = message.payload.decode().strip()
        if not payload_str:
            return
        data = json.loads(payload_str)
        event_type = data.get("event")
        confidence = data.get("confidence")
        image = data.get("image")
        # 建立 event
        event = event_manager.create_event(
            uid=uid,
            event_type=event_type,
            confidence=confidence,
            image=image
        )
        logger.info(
            f"[EVENT] {uid} {event_type} conf={confidence}"
        )
        #print(f"[EVENT] {uid} {event_type} conf={confidence}") 

    except Exception as e:
        logger.error(f"[EVENT Error] {e}")
