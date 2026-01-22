from datetime import datetime, timedelta
from typing import Dict
from app.models.device import Device


class DeviceRegistry:
    def __init__(self):
        self.devices: Dict[str, Device] = {}

    def register(self, device: Device):
        self.devices[device.id] = device

    def update_last_seen(self, device_id: str):
        device = self.devices.get(device_id)
        if not device:
            return

        device.last_seen = datetime.utcnow()
        device.status = "online"

    def mark_offline(self, device_id: str):
        device = self.devices.get(device_id)
        if device:
            device.status = "offline"

    def check_stale_devices(self):
        now = datetime.utcnow()

        for device in self.devices.values():
            if not device.last_seen:
                continue

            timeout = timedelta(seconds=device.heartbeat_interval * 2)

            if device.status == "online" and now - device.last_seen > timeout:
                device.status = "stale"

    # 
    def list_devices(self):
        return {
            device_id: {
                "type": device.type,
                "status": device.status,
                "last_seen": device.last_seen.isoformat()
                if device.last_seen else None,
                "heartbeat_interval": device.heartbeat_interval,
            }
            for device_id, device in self.devices.items()
        }

