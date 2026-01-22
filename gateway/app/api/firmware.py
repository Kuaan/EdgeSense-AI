from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/ota/firmware", tags=["OTA"])

FIRMWARE_DIR = "/home/pi/gateway/firmware"


@router.api_route("/{version}.bin", methods=["GET", "HEAD"])
def get_firmware(version: str):
    path = os.path.join(FIRMWARE_DIR, f"{version}.bin")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="firmware not found")

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=f"{version}.bin"
    )
