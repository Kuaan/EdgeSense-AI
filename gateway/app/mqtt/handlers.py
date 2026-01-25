#v8.0
import json
from app.models.device import Device
from app.core.device_registry import registry

def normalize_uid(uid: str) -> str:
    """統一 UID 格式：去掉冒號，轉大寫"""
    return uid.replace(":", "").upper()

def on_heartbeat(client, userdata, message):
    """
    Paho MQTT callback
    Topic: devices/{device_id}/heartbeat
    """
    try:
        topic = message.topic
        uid = normalize_uid(topic.split("/")[1])

        device = registry.devices.get(uid)
        if not device:
            # 自動註冊一個基本 device
            device = Device(uid=uid, model="esp32")
            registry.register(device)
            print(f"[Heartbeat] Auto-registered {uid}")

        registry.update_last_seen(uid)
        print(f"[Heartbeat] {uid}")

    except Exception as e:
        print(f"[Heartbeat Error] {e}")

def on_ota_status(client, userdata, message):
    """
    Paho MQTT callback
    Topic: devices/{device_id}/ota_status
    Payload: JSON {"status": "...", "fw_version": "...", "ts": ...}
    """
    try:
        topic = message.topic
        uid = normalize_uid(topic.split("/")[1])
        device = registry.devices.get(uid)
        if not device:
            print(f"[OTA Status] Unknown device {uid}")
            return

        data = json.loads(message.payload.decode())
        status = data.get("status")
        fw_version = data.get("fw_version")

        if status:
            device.status = status  # downloading / flashing / success / failed

        if fw_version and status == "success":
            device.fw_version = fw_version

        print(f"[OTA Status] {uid} → status={device.status}, fw_version={device.fw_version}")

    except Exception as e:
        print(f"[OTA Status Error] {e}")


'''v5.3
from app.core.device_registry import registry
from app.mqtt import topics


def on_heartbeat(topic: str, payload: bytes):
    """
    Topic: devices/{device_id}/heartbeat
    """
    try:
        parts = topic.split("/")
        if len(parts) < 3:
            raise ValueError(f"Invalid topic: {topic}")

        uid = topic.split("/")[1]
        registry.update_last_seen(uid)


        print(f"[Heartbeat] {uid}")

    except Exception as e:
        print(f"[Heartbeat Error] {e}")
'''

'''bf v5.3
from app.core.device_registry import registry
from app.mqtt import topics


def on_heartbeat(topic: str, payload: bytes):
    """
    Topic: devices/{device_id}/heartbeat
    """
    try:
        parts = topic.split("/")
        if len(parts) < 3:
            raise ValueError(f"Invalid topic: {topic}")

        device_id = parts[1]

        registry.update_last_seen(device_id)

        print(f"[Heartbeat] {device_id}")

    except Exception as e:
        print(f"[Heartbeat Error] {e}")

'''
