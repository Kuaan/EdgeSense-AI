from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class Device(BaseModel):
    id: str
    type: str
    status: Literal["online", "offline", "stale"] = "offline"
    last_seen: datetime | None = None
    heartbeat_interval: int = 10  # seconds

