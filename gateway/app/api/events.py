# app/api/events.py
from fastapi import APIRouter
from app.core.event_manager import event_manager

router = APIRouter()
# =========================================================
# List all events
# =========================================================
@router.get("/api/events")
def list_events():
    return {
        "events": event_manager.list_events()
    }

# =========================================================
# List events by device UID
# =========================================================
@router.get("/api/events/{uid}")
def list_events_by_uid(uid: str):
    return {
        "events": event_manager.list_events_by_uid(uid)
    }
