from fastapi import APIRouter
import psutil
import platform

router = APIRouter()

@router.get("/info")
def system_info():
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "cpu_usage": psutil.cpu_percent(),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage("/")._asdict(),
    }
