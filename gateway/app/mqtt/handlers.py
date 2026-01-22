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
