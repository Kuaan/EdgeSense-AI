# app/core/event_manager.py
from typing import List
from app.models.event import Event

class EventManager:
    def __init__(self):
        # 暫存在 memory
        # 未來可換成 database
        self.events: List[Event] = []

    # 建立事件
    def create_event(
        self,
        uid: str,
        event_type: str,
        confidence: float = None,
        image: str = None
    ) -> Event:
        event = Event(
            uid=uid,
            event_type=event_type,
            confidence=confidence,
            image=image
        )
        self.events.insert(0, event)
        return event

    # 取得所有事件
    def list_events(self):
        return [e.to_dict() for e in self.events]

    # 取得某 device 事件
    def list_events_by_uid(self, uid: str):
        return [
            e.to_dict()
            for e in self.events
            if e.uid == uid
        ]


# 全域 instance
event_manager = EventManager()
