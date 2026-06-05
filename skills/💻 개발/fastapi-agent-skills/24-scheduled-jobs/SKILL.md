---
name: scheduled-jobs
description: |
  APScheduler, Celery Beat를 활용한 정기 작업 스케줄링을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Scheduled Jobs Skill

APScheduler, Celery Beat를 활용한 정기 작업 스케줄링을 구현합니다.

## Triggers

- "스케줄링", "scheduled job", "cron", "정기 작업", "apscheduler"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |

---

## Output

### APScheduler Setup

```python
# app/infrastructure/scheduler/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings

import structlog

logger = structlog.get_logger()

# Job stores configuration
jobstores = {
    "default": RedisJobStore(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    ),
}

# Executors configuration
executors = {
    "default": AsyncIOExecutor(),
}

# Job defaults
job_defaults = {
    "coalesce": True,  # Combine multiple pending executions
    "max_instances": 1,  # Only one instance per job
    "misfire_grace_time": 60,  # Seconds to wait before considering misfire
}

# Create scheduler
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="UTC",
)


async def start_scheduler() -> None:
    """Start the scheduler."""
    if not scheduler.running:
        scheduler.start()
        await logger.ainfo("Scheduler started")


async def shutdown_scheduler() -> None:
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        await logger.ainfo("Scheduler stopped")
```

### Scheduled Jobs

```python
# app/infrastructure/scheduler/jobs.py
from datetime import datetime, timezone

import structlog

from app.infrastructure.scheduler.scheduler import scheduler

logger = structlog.get_logger()


# Job functions
async def cleanup_expired_sessions() -> None:
    """Clean up expired sessions from database."""
    await logger.ainfo("Running session cleanup job")

    # Import here to avoid circular imports
    from app.infrastructure.database.session import async_session_factory

    async with async_session_factory() as session:
        # Delete expired sessions
        from sqlalchemy import delete, text

        result = await session.execute(
            text("DELETE FROM sessions WHERE expires_at < NOW()")
        )
        await session.commit()

        await logger.ainfo(
            "Session cleanup completed",
            deleted_count=result.rowcount,
        )


async def send_daily_digest() -> None:
    """Send daily digest emails to users."""
    await logger.ainfo("Running daily digest job")

    # Implementation here
    pass


async def sync_external_data() -> None:
    """Sync data from external API."""
    await logger.ainfo("Running external data sync job")

    # Implementation here
    pass


async def generate_reports() -> None:
    """Generate periodic reports."""
    await logger.ainfo("Running report generation job")

    # Implementation here
    pass


async def health_check() -> None:
    """Periodic health check."""
    await logger.ainfo(
        "Health check",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Register jobs
def register_jobs() -> None:
    """Register all scheduled jobs."""

    # Cleanup expired sessions - every hour
    scheduler.add_job(
        cleanup_expired_sessions,
        trigger=IntervalTrigger(hours=1),
        id="cleanup_sessions",
        name="Cleanup Expired Sessions",
        replace_existing=True,
    )

    # Daily digest - every day at 9 AM UTC
    scheduler.add_job(
        send_daily_digest,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_digest",
        name="Send Daily Digest",
        replace_existing=True,
    )

    # Sync external data - every 15 minutes
    scheduler.add_job(
        sync_external_data,
        trigger=IntervalTrigger(minutes=15),
        id="sync_external",
        name="Sync External Data",
        replace_existing=True,
    )

    # Generate reports - every Monday at 6 AM UTC
    scheduler.add_job(
        generate_reports,
        trigger=CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="weekly_reports",
        name="Generate Weekly Reports",
        replace_existing=True,
    )

    # Health check - every 5 minutes
    scheduler.add_job(
        health_check,
        trigger=IntervalTrigger(minutes=5),
        id="health_check",
        name="Health Check",
        replace_existing=True,
    )


def unregister_jobs() -> None:
    """Remove all jobs."""
    for job in scheduler.get_jobs():
        job.remove()
```

### Lifespan Integration

```python
# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.infrastructure.scheduler.scheduler import (
    scheduler,
    start_scheduler,
    shutdown_scheduler,
)
from app.infrastructure.scheduler.jobs import register_jobs, unregister_jobs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    register_jobs()
    await start_scheduler()

    yield

    # Shutdown
    unregister_jobs()
    await shutdown_scheduler()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    # ... rest of setup
    return app
```

### Job Management API

```python
# app/api/v1/routes/scheduler.py
from datetime import datetime
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.v1.dependencies import SuperUser
from app.infrastructure.scheduler.scheduler import scheduler

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


class JobInfo(BaseModel):
    """Job information response."""

    id: str
    name: str
    next_run_time: datetime | None
    trigger: str


class AddJobRequest(BaseModel):
    """Add job request."""

    job_id: str
    job_type: str  # interval, cron, date
    # Interval trigger
    hours: int | None = None
    minutes: int | None = None
    seconds: int | None = None
    # Cron trigger
    cron_expression: str | None = None
    # Date trigger
    run_date: datetime | None = None


@router.get("/jobs", response_model=list[JobInfo])
async def list_jobs(_: SuperUser):
    """List all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append(
            JobInfo(
                id=job.id,
                name=job.name or job.id,
                next_run_time=job.next_run_time,
                trigger=str(job.trigger),
            )
        )
    return jobs


@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str, _: SuperUser):
    """Get specific job info."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobInfo(
        id=job.id,
        name=job.name or job.id,
        next_run_time=job.next_run_time,
        trigger=str(job.trigger),
    )


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str, _: SuperUser):
    """Pause a scheduled job."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.pause()
    return {"message": f"Job {job_id} paused"}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str, _: SuperUser):
    """Resume a paused job."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.resume()
    return {"message": f"Job {job_id} resumed"}


@router.post("/jobs/{job_id}/run")
async def run_job_now(job_id: str, _: SuperUser):
    """Run a job immediately."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Add a one-time job to run immediately
    scheduler.add_job(
        job.func,
        trigger=DateTrigger(run_date=datetime.now()),
        id=f"{job_id}_manual",
        replace_existing=True,
    )

    return {"message": f"Job {job_id} triggered"}


@router.delete("/jobs/{job_id}")
async def remove_job(job_id: str, _: SuperUser):
    """Remove a scheduled job."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.remove()
    return {"message": f"Job {job_id} removed"}


@router.post("/jobs/{job_id}/reschedule")
async def reschedule_job(
    job_id: str,
    request: AddJobRequest,
    _: SuperUser,
):
    """Reschedule a job with new trigger."""
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if request.job_type == "interval":
        trigger = IntervalTrigger(
            hours=request.hours or 0,
            minutes=request.minutes or 0,
            seconds=request.seconds or 0,
        )
    elif request.job_type == "cron":
        trigger = CronTrigger.from_crontab(request.cron_expression)
    elif request.job_type == "date":
        trigger = DateTrigger(run_date=request.run_date)
    else:
        raise HTTPException(status_code=400, detail="Invalid job type")

    job.reschedule(trigger=trigger)
    return {"message": f"Job {job_id} rescheduled"}
```

### Job Execution Tracking

```python
# app/infrastructure/scheduler/tracking.py
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.base import BaseModel as DBBaseModel


class JobStatus(str, Enum):
    """Job execution status."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class JobExecutionModel(DBBaseModel):
    """Job execution history model."""

    __tablename__ = "job_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(100), index=True)
    job_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobExecutionTracker:
    """Track job executions."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def start_execution(
        self,
        job_id: str,
        job_name: str,
    ) -> int:
        """Record job execution start."""
        async with self._session_factory() as session:
            execution = JobExecutionModel(
                job_id=job_id,
                job_name=job_name,
                status=JobStatus.RUNNING.value,
                started_at=datetime.now(timezone.utc),
            )
            session.add(execution)
            await session.commit()
            await session.refresh(execution)
            return execution.id

    async def complete_execution(
        self,
        execution_id: int,
        success: bool = True,
        error_message: str | None = None,
    ) -> None:
        """Record job execution completion."""
        async with self._session_factory() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(JobExecutionModel).where(
                    JobExecutionModel.id == execution_id
                )
            )
            execution = result.scalar_one_or_none()

            if execution:
                execution.status = (
                    JobStatus.SUCCESS.value if success else JobStatus.FAILED.value
                )
                execution.finished_at = datetime.now(timezone.utc)
                execution.duration_ms = int(
                    (execution.finished_at - execution.started_at).total_seconds()
                    * 1000
                )
                execution.error_message = error_message
                await session.commit()

    async def get_recent_executions(
        self,
        job_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get recent job executions."""
        async with self._session_factory() as session:
            from sqlalchemy import select

            query = select(JobExecutionModel).order_by(
                JobExecutionModel.started_at.desc()
            )

            if job_id:
                query = query.where(JobExecutionModel.job_id == job_id)

            query = query.limit(limit)
            result = await session.execute(query)

            return [
                {
                    "id": e.id,
                    "job_id": e.job_id,
                    "job_name": e.job_name,
                    "status": e.status,
                    "started_at": e.started_at,
                    "finished_at": e.finished_at,
                    "duration_ms": e.duration_ms,
                    "error_message": e.error_message,
                }
                for e in result.scalars().all()
            ]
```

### Job Decorator with Tracking

```python
# app/infrastructure/scheduler/decorators.py
import functools
from typing import Callable

import structlog

from app.infrastructure.database.session import async_session_factory
from app.infrastructure.scheduler.tracking import JobExecutionTracker

logger = structlog.get_logger()
tracker = JobExecutionTracker(async_session_factory)


def tracked_job(job_id: str, job_name: str):
    """Decorator to track job execution."""

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            execution_id = await tracker.start_execution(job_id, job_name)

            try:
                result = await func(*args, **kwargs)
                await tracker.complete_execution(execution_id, success=True)
                return result

            except Exception as e:
                await logger.aexception(
                    "Job execution failed",
                    job_id=job_id,
                    error=str(e),
                )
                await tracker.complete_execution(
                    execution_id,
                    success=False,
                    error_message=str(e),
                )
                raise

        return wrapper

    return decorator


# Usage example
@tracked_job("cleanup_sessions", "Cleanup Expired Sessions")
async def cleanup_expired_sessions() -> None:
    """Clean up expired sessions."""
    # Job logic here
    pass
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Redis (for job store)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
```

### Dependencies

```toml
# Add to pyproject.toml
dependencies = [
    # ... existing ...
    "apscheduler>=3.10.0",
]
```

## Cron Expression Reference

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 9 * * *` | Every day at 9 AM |
| `0 0 * * 0` | Every Sunday at midnight |
| `0 0 1 * *` | First day of every month |
| `*/15 * * * *` | Every 15 minutes |
| `0 9-17 * * 1-5` | Every hour 9-17, Mon-Fri |

## References

- `_references/ARCHITECTURE-PATTERN.md`
