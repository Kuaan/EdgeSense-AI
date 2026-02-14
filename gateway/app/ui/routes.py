# v8.5 app/ui/routes.py
import os
import json
import time
import socket

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.device_registry import registry
from app.core.ota_jobs import OTA_JOBS as ota_jobs
from app.mqtt.client import mqtt_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================
# Helper: 自動取得 Gateway IP
# =========================
def get_gateway_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # 不會真的發包
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# =========================
# Dashboard
# =========================
@router.get("/")
def dashboard(request: Request):
    devices = list(registry.devices.values())
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "devices": devices,
        }
    )


# =========================
# Device Detail
# =========================
@router.get("/devices/{uid}")
def device_detail(request: Request, uid: str):
    # 取得 device
    device = registry.devices.get(uid)
    if not device:
        return templates.TemplateResponse(
            "device_not_found.html",
            {"request": request, "uid": uid},
            status_code=404
        )

    # 該 device 的 OTA jobs
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
        }
    )


# =========================
# OTA Start
# =========================
@router.post("/devices/{uid}/ota")
def ota_start(uid: str, version: str = Form(...)):
    job_id = f"ota-{int(time.time())}"

    # OTA Job 記錄
    ota_jobs[job_id] = {
        "job_id": job_id,
        "uid": uid,
        "version": version,
        "status": "started",
        "ts": int(time.time())
    }

    # Firmware URL for ESP32
    gateway_ip = get_gateway_ip()
    firmware_url = f"http://{gateway_ip}:8000/firmware/{version}"

    # MQTT publish
    mqtt_client.publish(
        f"devices/{uid}/ota",
        json.dumps({
            "job_id": job_id,
            "version": version,
            "url": firmware_url,  # ESP32 下載用
        })
    )

    return RedirectResponse(
        url=f"/devices/{uid}",
        status_code=303
    )




'''#v8.4 app/ui/routes.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.device_registry import registry
from app.core.ota_jobs import OTA_JOBS as ota_jobs

from app.mqtt.client import mqtt_client

import json
import time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# =========================
# Dashboard
# =========================
@router.get("/")
def dashboard(request: Request):
    devices = list(registry.devices.values())
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "devices": devices,
        }
    )

# =========================
# Device Detail
# =========================
@router.get("/devices/{uid}")
def device_detail(request: Request, uid: str):
    # 修正：直接從 dict 拿
    device = registry.devices.get(uid)
    jobs = [
        job
        for job in ota_jobs.values()
        if job["uid"] == uid
    ]
    return templates.TemplateResponse(
        "device_detail.html",
        {
            "request": request,
            "device": device,
            "jobs": jobs,
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
        }
    )

# =========================
# OTA Start
# =========================
@router.post("/devices/{uid}/ota")
def ota_start(uid: str, version: str = Form(...)):
    job_id = f"ota-{int(time.time())}"
    # 修正：使用 ota_jobs（alias）
    ota_jobs[job_id] = {
        "job_id": job_id,
        "uid": uid,
        "version": version,
        "status": "started",
        "ts": int(time.time())
    }
    mqtt_client.publish(
        f"devices/{uid}/ota",
        json.dumps({
            "job_id": job_id,
            "version": version,
        })
    )
    return RedirectResponse(
        url=f"/devices/{uid}",
        status_code=303
    )
'''


'''#8.2 app/ui/routes.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

#from app.core.device_registry import registry as device_registry
from app.core.device_registry import registry


from app.core.ota_jobs import OTA_JOBS as ota_jobs


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request):
    devices = list(registry.devices.values())
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "devices": devices,
        }
    )


@router.get("/devices/{uid}")
def device_detail(request: Request, uid: str):
    device = registry.get(uid)
    # 過濾 dict 取得該 device 的 jobs
    jobs = [job for job in ota_jobs.values() if job["uid"] == uid]
    return templates.TemplateResponse(
        "device_detail.html",
        {
            "request": request,
            "device": device,
            "jobs": jobs,
        }
    )


@router.get("/ota/jobs")
def ota_jobs_page(request: Request):
    jobs = list(ota_jobs.values())
    return templates.TemplateResponse(
        "ota_jobs.html",
        {
            "request": request,
            "jobs": jobs,
        }
    )
'''
