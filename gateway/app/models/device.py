#v8.1
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

'''#v8.0
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class Device(BaseModel):
    uid: str                 # MAC / chip id (唯一)
    model: str               # esp32 / esp32s3
    name: str | None = None  # esp32-001 (gateway assign)

    # 狀態包含 Heartbeat 與 OTA 狀態
    status: Literal[
        "online", "offline", "stale",
        "downloading", "flashing", "success", "failed"
    ] = "offline"

    fw_version: str | None = None   # 新增 OTA fw_version

    last_seen: datetime | None = None
    heartbeat_interval: int = 10
'''

'''v5.3
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class Device(BaseModel):
    uid: str                 # MAC / chip id (唯一)
    model: str              # esp32 / esp32s3
    name: str | None = None # esp32-001 (gateway assign)

    status: Literal["online", "offline", "stale"] = "offline"
    last_seen: datetime | None = None
    heartbeat_interval: int = 10
'''

'''bf v5.3
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class Device(BaseModel):
    id: str
    type: str
    status: Literal["online", "offline", "stale"] = "offline"
    last_seen: datetime | None = None
    heartbeat_interval: int = 10  # seconds

'''
