#v1.1.12 app/models/device.py
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any

class Device(BaseModel):
    uid: str
    model: str
    name: str | None = None
    status: Literal["online", "offline", "stale", "downloading", "flashing", "success", "failed"] = "offline"
    fw_version: str | None = None
    last_seen: datetime = Field(default_factory=datetime.now)
    heartbeat_interval: int = 10

    last_ai_event: str | None = None
    last_ai_confidence: float | None = None
    last_ai_time: datetime | None = None
    last_ai_image_url: str | None = None
    ai_history: List[Dict[str, Any]] = []
    
    # ==========================================
    # ESP32 Gateway (LoRa) 
    # ==========================================
    sensor_data: str | None = None  # JSON  "data" 
    rssi: int | None = None         # JSON  "rssi"
    snr: float | None = None        # JSON  "snr"
