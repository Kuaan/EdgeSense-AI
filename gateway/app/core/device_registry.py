class DeviceRegistry:
    def __init__(self):
        self.devices = {}

    def register(self, device):
        self.devices[device.device_id] = device

    def list(self):
        return list(self.devices.values())

registry = DeviceRegistry()
