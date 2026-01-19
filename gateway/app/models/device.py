from pydantic import BaseModel
from typing import Optional

class Device(BaseModel):
    device_id: str
    device_type: str
    protocol: str
    firmware_version: Optional[str] = None
    status: str = "offline"

