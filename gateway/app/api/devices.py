from fastapi import APIRouter 
from app.models.device import Device 
from app.core.device_registry import registry

router = APIRouter()

@router.post("/register")
def register_device(device: Device):
    registry.register(device)
    return {"result": "ok"}

@router.get("/")
def list_devices():
    return registry.list()
