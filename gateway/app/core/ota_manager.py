# v10.0 Industrial OTA Manager

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

        # Prevent duplicate job unless force

        if not force:

            active = self.get_active_job(uid)

            if active:

                return active


        job = OTAJob(uid, version, force)


        self.jobs[job.job_id] = job


        # register to OTA_JOBS (used by mqtt handler)

        OTA_JOBS[job.job_id] = {

            "job_id": job.job_id,

            "uid": uid,

            "version": version,

            "status": "sent",

            "created_at": job.created_at,

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

        job = self.jobs.get(job_id)

        if not job:

            return


        job.status = status

        job.updated_at = time.time()


        if status in ["success", "failed"]:

            job.completed_at = job.updated_at

            job.result = status


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



'''# v9.0 app/core/ota_manager.py

import time
import uuid

class OTAJob:
    def __init__(self, uid, version):
        self.job_id = str(uuid.uuid4())[:8]
        self.uid = uid
        self.version = version
        self.status = "created"
        self.ts = time.time()
        self.retry = 0

class OTAManager:
    def __init__(self):
        self.jobs = []

    def create_job(self, uid, version):
        job = OTAJob(uid, version)
        self.jobs.append(job)
        return job

    def get_jobs(self, uid):
        return [j for j in self.jobs if j.uid == uid]

    def get_active_job(self, uid):
        for j in reversed(self.jobs):
            if j.uid == uid and j.status not in ["success", "failed"]:
                return j
        return None

    def update_status(self, uid, status):
        job = self.get_active_job(uid)
        if job:
            job.status = status

ota_manager = OTAManager()
'''
