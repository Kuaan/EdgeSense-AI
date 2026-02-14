#v8.5
from fastapi import APIRouter, HTTPException
from app.models.device import Device
from app.core.device_registry import registry

router = APIRouter()


@router.post("/devices/register")
def register_device(device: Device):
    if device.uid in registry.devices:
        raise HTTPException(status_code=409, detail="Device already registered")

    registry.register(device)
    return {"result": "ok"}


@router.get("/devices")
def get_devices():
    return registry.list()
