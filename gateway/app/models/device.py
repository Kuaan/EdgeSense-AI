#v8.5
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class Device(BaseModel):
    uid: str
    model: str
    name: str | None = None
    status: Literal[
        "online", "offline", "stale",
        "downloading", "flashing", "success", "failed"
    ] = "offline"
    fw_version: str | None = None
    # 使用 Field 確保預設值生成方式正確
    last_seen: datetime = Field(default_factory=datetime.now)
    heartbeat_interval: int = 10