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
