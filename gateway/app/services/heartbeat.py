import asyncio
from app.core.device_registry import DeviceRegistry

async def heartbeat_watcher(registry: DeviceRegistry):
    while True:
        registry.check_stale_devices()
        await asyncio.sleep(5)
