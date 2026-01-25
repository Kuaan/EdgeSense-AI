


#v8.0
import time
from app.models.device import Device

class DeviceRegistry:
    def __init__(self):
        self.devices: dict[str, Device] = {}

    def register(self, device: Device):
        self.devices[device.uid] = device
        device.last_seen = time.time()
        device.status = "online"

    def list(self):
        return list(self.devices.values())

    def update_last_seen(self, uid: str):
        device = self.devices.get(uid)
        if not device:
            return
        device.last_seen = time.time()
        # Heartbeat online 不會覆蓋 OTA 狀態
        if device.status not in ["downloading","flashing","success","failed"]:
            device.status = "online"

    def check_stale_devices(self, timeout_sec: int = 30):
        now = time.time()
        for device in self.devices.values():
            last_seen = getattr(device, "last_seen", None)
            if last_seen is None:
                continue
            if now - last_seen > timeout_sec:
                if device.status != "offline":
                    device.status = "offline"
                    print(f"[Heartbeat] {device.uid} marked offline")

registry = DeviceRegistry()


'''v5.3
import time


class DeviceRegistry:
    def __init__(self):
        self.devices = {}

    def register(self, device):
        self.devices[device.uid] = device   # ✅ 統一用 uid
        device.last_seen = time.time()
        device.status = "online"

    def list(self):
        return list(self.devices.values())

    def update_last_seen(self, uid: str):
        device = self.devices.get(uid)
        if not device:
            return

        device.last_seen = time.time()
        device.status = "online"

    def check_stale_devices(self, timeout_sec: int = 30):
        now = time.time()

        for device in self.devices.values():
            last_seen = getattr(device, "last_seen", None)
            if last_seen is None:
                continue

            if now - last_seen > timeout_sec:
                if device.status != "offline":
                    device.status = "offline"
                    print(f"[Heartbeat] {device.uid} marked offline")


registry = DeviceRegistry()
'''

'''v5.0
import time
class DeviceRegistry:
    def __init__(self):
        self.devices = {}

    def register(self, device):
        self.devices[device.device_id] = device
        device.last_seen = time.time()
        device.status = "online"

    def list(self):
        return list(self.devices.values())

    # ✅ heartbeat 進來時呼叫
    def update_last_seen(self, device_id: str):
        device = self.devices.get(device_id)
        if not device:
            return

        device.last_seen = time.time()
        device.status = "online"

    # ✅ heartbeat watcher 用
    def check_stale_devices(self, timeout_sec: int = 30):
        now = time.time()

        for device in self.devices.values():
            last_seen = getattr(device, "last_seen", None)
            if last_seen is None:
                continue

            if now - last_seen > timeout_sec:
                if device.status != "offline":
                    device.status = "offline"
                    print(f"[Heartbeat] {device.device_id} marked offline")


# ✅ 全系統唯一 instance
registry = DeviceRegistry()

'''
