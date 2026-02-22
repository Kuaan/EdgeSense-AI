# app/models/event.py
import time

class Event:
    def __init__(
        self,
        uid: str,
        event_type: str,
        confidence: float = None,
        image: str = None,
        timestamp: float = None
    ):

        self.uid = uid
        self.event_type = event_type
        self.confidence = confidence
        self.image = image
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            "uid": self.uid,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "image": self.image,
            "timestamp": self.timestamp
        }