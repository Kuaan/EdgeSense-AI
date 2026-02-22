#v10.0 app/api/ui/routes.py
import os
import json
import time
import socket

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.device_registry import registry
from app.core.event_manager import event_manager
from app.core.ota_jobs import OTA_JOBS as ota_jobs
from app.mqtt.client import mqtt_client

from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# -------------------------
# Helper: 自動取得 Gateway IP
# -------------------------
def get_gateway_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# -------------------------
# Friendly time
# -------------------------
def friendly_time(ts):
    """將 datetime 或 timestamp 轉成友善時間文字"""
    # 如果傳入的是 datetime 物件，轉成 timestamp
    if isinstance(ts, datetime):
        ts = ts.timestamp()
    diff = int(time.time() - ts)
    if diff < 60:
        return f"{diff}s ago"
    elif diff < 3600:
        return f"{diff//60}m ago"
    else:
        return f"{diff//3600}h ago"


# =========================
# Dashboard
# =========================
@router.get("/")
def dashboard(request: Request):
    devices = list(registry.devices.values())
    events = event_manager.list_events() #
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "devices": devices,
            "events": events, #
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
        return templates.TemplateResponse(
            "device_not_found.html",
            {"request": request, "uid": uid},
            status_code=404
        )

    # OTA jobs for this device
    jobs = [job for job in ota_jobs.values() if job["uid"] == uid]

    # firmware list .bin only
    firmware_dir = "firmware"
    firmware_list = sorted([f for f in os.listdir(firmware_dir) if f.endswith(".bin")])

    return templates.TemplateResponse(
        "device_detail.html",
        {
            "request": request,
            "device": device,
            "jobs": jobs,
            "firmware_list": firmware_list,
            "friendly_time": friendly_time
        }
    )


# =========================
# OTA Job List
# =========================
@router.get("/ota/jobs")
def ota_jobs_page(request: Request):
    jobs = list(ota_jobs.values())
    return templates.TemplateResponse(
        "ota_jobs.html",
        {
            "request": request,
            "jobs": jobs,
            "friendly_time": friendly_time
        }
    )


# =========================
# OTA Start
# =========================
@router.post("/devices/{uid}/ota")
def ota_start(uid: str, version: str = Form(...), force: bool = Form(False)):
    job_id = f"ota-{int(time.time())}"

    ota_jobs[job_id] = {
        "job_id": job_id,
        "uid": uid,
        "version": version,
        "status": "started",
        "ts": int(time.time()),
        "force": force
    }

    gateway_ip = get_gateway_ip()
    firmware_url = f"http://{gateway_ip}:8000/firmware/{version}"

    mqtt_client.publish(
        f"devices/{uid}/ota",
        json.dumps({
            "job_id": job_id,
            "version": version,
            "url": firmware_url,
            "force": force
        })
    )

    return RedirectResponse(
        url=f"/devices/{uid}",
        status_code=303
    )


# =========================
# Reset Device Status
# =========================
@router.post("/devices/{uid}/reset")
def reset_device(uid: str):
    device = registry.devices.get(uid)
    if device:
        device.status = "online"
    return RedirectResponse(
        url=f"/devices/{uid}",
        status_code=303
    )
