#v1.1.13 app/mqtt/handlers.py

import json
import logging
import time
from datetime import datetime
from app.models.device import Device
from app.core.ota_jobs import OTA_JOBS
from app.core.device_registry import registry
from app.core.event_manager import event_manager 

logger = logging.getLogger(__name__)

def normalize_uid(uid: str) -> str:
    """ UID formate：remove":", uppercase"""
    if not uid: return "UNKNOWN"
    return uid.replace(":", "").upper().strip()

# =========================================================
# 1. Heartbeat Handler
# =========================================================
def on_heartbeat(client, userdata, message):
    try:
        parts = message.topic.split("/")
        if len(parts) < 2: return
        uid = normalize_uid(parts[1])
        
        if uid not in registry.devices:
            new_dev = Device(uid=uid, model="esp32-node", status="online")
            registry.register(new_dev)
            logger.info(f"🆕 [Auto-Register] Heartbeat from new device: {uid}")
        
        registry.update_last_seen(uid)
        logger.info(f"💓 [Heartbeat] {uid}")
    except Exception as e:
        logger.error(f"❌ [Heartbeat Error] {e}")

# =========================================================
# 2. OTA Status Handler
# =========================================================
def on_ota_status(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        job_id = payload.get("job_id")
        status = payload.get("status")
        
        if not job_id: return

        from app.core.ota_manager import ota_manager
        ota_manager.update_status(job_id, status)
        
        logger.info(f"✅ [MQTT] OTA Job {job_id} status changed to: {status}")
    except Exception as e:
        logger.error(f"❌ [OTA Status Error] {e}")
        
# =========================================================
# 3. Event Handler (AI & LoRa)
# =========================================================
def on_event(client, userdata, message):
    uid = "UNKNOWN"
    try:
        # 0. parse Topic, get UID
        parts = message.topic.split("/")
        if len(parts) < 2: return
        uid = normalize_uid(parts[1])

        # 1. get the original Byte and decoding
        raw_payload = message.payload.decode('utf-8', errors='ignore')
        
        # 2. keep the first context
        start_idx = raw_payload.find('{')
        end_idx = raw_payload.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            logger.error(f"❌ [MQTT] Invalid JSON structure from {uid}")
            return
            
        clean_json = raw_payload[start_idx:end_idx + 1]
        
        # 3. parse the JSON after cleaning
        data = json.loads(clean_json)
        
        # 4. auto-registry
        if uid not in registry.devices:
            m_type = "stm32-lora" if "data" in data else "esp32-s3-cam"
            device = Device(uid=uid, model=m_type, status="online")
            registry.register(device)
            logger.info(f"🆕 [Auto-Register] Event from {m_type}: {uid}")
        
        device = registry.devices.get(uid)

        # ---  LoRa data (STM32 channel) ---
        if "data" in data:
            device.sensor_data = data.get("data")
            device.rssi = data.get("rssi")
            device.snr = data.get("snr")
            device.last_seen = datetime.now()
            device.model = "stm32-lora" 
            logger.info(f"📡 [LoRa Data] {uid}: {device.sensor_data}")

        # --- handle AI event (ESP32-S3 CAM channel) ---
        if "event" in data:
            event_obj = event_manager.create_event(
                uid=uid,
                event_type=data.get("event"),
                confidence=data.get("confidence", 0.0),
                image=data.get("image")
            )
            event_manager.process_ai_logic(event_obj)

            img_filename = getattr(event_obj, 'image_filename', None)
            
            # update device status
            device.model = "esp32-s3-cam"
            device.last_ai_event = data.get("event")
            device.last_ai_confidence = data.get("confidence", 0.0)
            device.last_ai_time = datetime.now() 
            
            if img_filename:
                device.last_ai_image_url = f"/static/captures/{img_filename}"
                
                # update the history of devices
                if not hasattr(device, 'ai_history'): device.ai_history = []
                device.ai_history.insert(0, {
                    "url": device.last_ai_image_url, 
                    "time": device.last_ai_time.strftime("%H:%M:%S")
                })
                device.ai_history = device.ai_history[:5]
                logger.info(f"📸 [AI Sync] {uid} matched image: {img_filename}")
            else:
                logger.warning(f"⚠️ [AI Sync] No image filename for {uid}")

    except Exception as e:
        logger.error(f"❌ [Event Error] Device {uid}: {e}")
