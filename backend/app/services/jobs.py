import uuid
from datetime import datetime

from app.models.schemas import JobStatus


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, JobStatus] = {}

    def create(self, message: str = "Queued") -> JobStatus:
        job = JobStatus(
            job_id=uuid.uuid4().hex,
            status="queued",
            stage="queued",
            progress=0,
            message=message,
            started_at=datetime.utcnow(),
        )
        self._jobs[job.job_id] = job
        return job

    def update(self, job_id: str, **changes) -> JobStatus:
        job = self._jobs[job_id]
        updated = job.model_copy(update=changes)
        self._jobs[job_id] = updated
        return updated

    def get(self, job_id: str) -> JobStatus | None:
        return self._jobs.get(job_id)

    def latest(self) -> list[JobStatus]:
        return sorted(self._jobs.values(), key=lambda job: job.started_at, reverse=True)[:20]


job_manager = JobManager()
