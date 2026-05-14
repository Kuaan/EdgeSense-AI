#v1.1.11 app/core/ota_manager.py

import time
import uuid

from app.core.ota_jobs import OTA_JOBS


# =========================================================
# OTA Job Object
# =========================================================

class OTAJob:

    def __init__(self, uid, version, force=False):
        self.job_id = str(uuid.uuid4())[:8]
        self.uid = uid
        self.version = version
        self.force = force
        self.status = "created"
        self.result = None
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.completed_at = None
        self.retry = 0
        self.timeout = 120   # seconds


# =========================================================
# OTA Manager
# =========================================================

class OTAManager:

    def __init__(self):
        self.jobs = {}


    # =====================================================
    # Create Job
    # =====================================================
    def create_job(self, uid, version, force=False):
        if not force:
            active = self.get_active_job(uid)
            if active:
                return active

        job = OTAJob(uid, version, force)
        self.jobs[job.job_id] = job

        OTA_JOBS[job.job_id] = {
            "job_id": job.job_id,
            "uid": uid,
            "version": version,
            "status": "sent",
            "ts": job.created_at,      
            "updated_at": job.created_at,
            "completed_at": None,
            "retry": 0
        }
        return job
    # =====================================================
    # Get Jobs by UID
    # =====================================================

    def get_jobs(self, uid):
        result = []

        for job_id, job in self.jobs.items():
            if job.uid == uid:
                result.append(job)

        return result


    # =====================================================
    # Active Job
    # =====================================================

    def get_active_job(self, uid):
        for job in reversed(list(self.jobs.values())):
            if job.uid != uid:
                continue

            if job.status in [
                "created",
                "sent",
                "downloading",
                "flashing"
            ]:

                return job

        return None


    # =====================================================
    # Update Status
    # =====================================================
    def update_status(self, job_id, status):
        # 1. update obj.
        job = self.jobs.get(job_id)
        if job:
            job.status = status
            job.updated_at = time.time()
            if status in ["success", "failed"]:
                job.completed_at = job.updated_at
                job.result = status

        # 2. update global dict. for UI
        if job_id in OTA_JOBS:
            OTA_JOBS[job_id]["status"] = status
            OTA_JOBS[job_id]["updated_at"] = time.time()
            if status in ["success", "failed"]:
                OTA_JOBS[job_id]["completed_at"] = time.time()
    


    # =====================================================
    # Timeout Checker
    # =====================================================

    def check_timeout(self):
        now = time.time()

        for job in self.jobs.values():
            if job.status not in [
                "sent",
                "downloading",
                "flashing"
            ]:
                continue


            if now - job.updated_at > job.timeout:
                job.status = "failed"
                job.result = "timeout"
                job.completed_at = now
                print(
                    f"[OTA] timeout job={job.job_id}"
                )


# =========================================================
# Global instance
# =========================================================

ota_manager = OTAManager()
