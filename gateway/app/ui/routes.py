#v1.1.13 app/api/ui/routes.py
import os
import json
import time
import socket
from datetime import datetime

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.device_registry import registry
from app.core.event_manager import event_manager
from app.core.ota_jobs import OTA_JOBS as ota_jobs
from app.core.ota_manager import ota_manager 
from app.mqtt.client import mqtt_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_gateway_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def friendly_time(ts):
    if ts is None: return "Never"
    try:
        if isinstance(ts, datetime):
            ts_val = ts.timestamp()
        else:
            ts_val = float(ts)
            
        diff = int(time.time() - ts_val)
        if diff < 0: return "Just now"
        if diff < 60: return f"{diff}s ago"
        elif diff < 3600: return f"{diff//60}m ago"
        elif diff < 86400: return f"{diff//3600}h ago"
        else: return datetime.fromtimestamp(ts_val).strftime("%m/%d %H:%M")
    except Exception:
        return "Unknown"

# =========================
# Dashboard 
# =========================
@router.get("/")
def dashboard(request: Request):
    devices_data = [d.dict() for d in registry.devices.values()]
    events = event_manager.list_events() 

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "devices": devices_data,
            "events": events,
            "friendly_time": friendly_time
        }
    )

# =========================
# Device Detail
# =========================
@router.get("/devices/{uid}")
def device_detail(request: Request, uid: str):
    device = registry.devices.get(uid)
    if not device:
        return templates.TemplateResponse("device_not_found.html", {"request": request, "uid": uid}, status_code=404)

    device_jobs = []
    for job in ota_jobs.values():
        if job.get("uid") == uid:
            j = job.copy()
            if "ts" not in j: j["ts"] = j.get("created_at", time.time())
            device_jobs.append(j)
    
    device_jobs.sort(key=lambda x: x.get('ts', 0), reverse=True)

    firmware_list = []
    if os.path.exists("firmware"):
        firmware_list = sorted([f for f in os.listdir("firmware") if f.endswith(".bin")], reverse=True)

    return templates.TemplateResponse(
        "device_detail.html",
        {
            "request": request,
            "device": device.dict(),
            "jobs": device_jobs,
            "firmware_list": firmware_list,
            "friendly_time": friendly_time
        }
    )

# =========================
# OTA Job List
# =========================
@router.get("/ota/jobs")
def ota_jobs_page(request: Request):
    all_jobs = []
    for job in ota_jobs.values():
        j = job.copy()
        if "ts" not in j: j["ts"] = j.get("created_at", time.time())
        all_jobs.append(j)

    all_jobs.sort(key=lambda x: x.get('ts', 0), reverse=True)
    return templates.TemplateResponse(
        "ota_jobs.html",
        {"request": request, "jobs": all_jobs, "friendly_time": friendly_time}
    )

# =========================
# OTA Start
# =========================
@router.post("/devices/{uid}/ota")
def ota_start(uid: str, version: str = Form(...), force: bool = Form(False)):
    job_obj = ota_manager.create_job(uid, version, force)
    
    gateway_ip = get_gateway_ip()
    mqtt_client.publish(
        f"devices/{uid}/ota",
        json.dumps({
            "job_id": job_obj.job_id, 
            "version": version,
            "url": f"http://{gateway_ip}:8000/firmware/{version}",
            "force": force
        })
    )
    return RedirectResponse(url=f"/devices/{uid}", status_code=303)

# =========================
# Reset Device Status
# =========================
@router.post("/devices/{uid}/reset")
def reset_device(uid: str):
    if uid in registry.devices:
        registry.devices[uid].status = "online"
    return RedirectResponse(url=f"/devices/{uid}", status_code=303)
