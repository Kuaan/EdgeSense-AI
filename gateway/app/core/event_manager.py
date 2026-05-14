#v1.1.13 app/core/event_manager.py
import os
import base64
import logging
import time
from typing import List
from datetime import datetime
from pathlib import Path  
from app.models.event import Event

logger = logging.getLogger(__name__)

class EventManager:
    def __init__(self):
        self.events: List[Event] = []

    def create_event(self, uid: str, event_type: str, confidence: float = None, image: str = None) -> Event:
        event = Event(
            uid=uid,
            event_type=event_type,
            confidence=confidence,
            image=image
        )
        # init timestamp 
        event.timestamp = time.time()
        
        self.events.insert(0, event)
        if len(self.events) > 100:
            self.events = self.events[:100]
        return event

    def list_events(self):
        return [e.to_dict() for e in self.events]

    def _cleanup_old_images(self, max_files: int = 100):
        try:
            save_dir = Path("static/captures")
            if not save_dir.exists(): return
            files = sorted(save_dir.glob("*.jpg"), key=os.path.getmtime)
            if len(files) > max_files:
                for f in files[:len(files) - max_files]:
                    os.remove(f)
        except Exception as e:
            logger.error(f"⚠️ [Cleanup Error]: {e}")

    def process_ai_logic(self, event: Event):
        if event.confidence is not None and event.confidence < 0.6:
            return

        image_url = None
        if event.image and len(event.image) > 10: 
            try:
                save_dir = Path("static/captures")
                save_dir.mkdir(parents=True, exist_ok=True)
                

                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{event.uid}_{timestamp_str}.jpg"
                filepath = save_dir / filename
                
                event.image_filename = filename 
                
                img_data = event.image
                if "," in img_data:
                    img_data = img_data.split(",")[1]
                
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(img_data))
                
                image_url = f"/static/captures/{filename}"
                logger.info(f"📸 [Storage] 影像存檔成功: {filename}")
                
                self._cleanup_old_images(max_files=100)
            except Exception as e:
                logger.error(f"❌ [Storage Error]: {e}")

        # update Registry
        from app.core.device_registry import registry
        device = registry.devices.get(event.uid) 
        
        if device:
            device.last_ai_event = event.event_type
            device.last_ai_confidence = event.confidence
            device.last_ai_time = datetime.now()
            device.last_ai_image_url = image_url

            new_history_entry = {
                "event": event.event_type,
                "confidence": event.confidence,
                "time": datetime.now().strftime("%H:%M:%S"),
                "url": image_url
            }
            
            if not hasattr(device, 'ai_history') or device.ai_history is None:
                device.ai_history = []
            
            device.ai_history.insert(0, new_history_entry)
            device.ai_history = device.ai_history[:6]
            logger.info(f"✅ [Registry] Device {event.uid} AI history updated.")

event_manager = EventManager()
