#v8.5 app/core/device_registry.py
import time
from datetime import datetime
from app.models.device import Device

class DeviceRegistry:
    def __init__(self):
        self.devices: dict[str, Device] = {}

    def register(self, device: Device):
        self.devices[device.uid] = device
        device.last_seen = datetime.now()
        device.status = "online"

    def update_last_seen(self, uid: str):
        device = self.devices.get(uid)
        if not device:
            return

        device.last_seen = datetime.now()
        if device.status in ["success", "failed", "offline"]:
            device.status = "online"

        elif device.status in ["downloading", "flashing"]:
            device.status = "online"
            print(f"[OTA] Device {uid} heartbeat received, status unlocked to online")

        else:
            device.status = "online"

    def check_stale_devices(self, timeout_sec: int = 30):
        now = datetime.now()
        for device in self.devices.values():
            if device.last_seen is None:
                continue
            delta = (now - device.last_seen).total_seconds()
            if delta > timeout_sec:
                if device.status != "offline":
                    device.status = "offline"
                    print(f"[Heartbeat] {device.uid} marked offline")

    # ⭐ UI需要
    def list(self):
        return list(self.devices.values())
        
    # ⭐ UI需要
    def get(self, uid: str):
        return self.devices.get(uid)

# ⭐ singleton
registry = DeviceRegistry()



