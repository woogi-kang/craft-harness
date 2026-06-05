---
name: background-tasks
description: |
  Celery, ARQ, FastAPI BackgroundTasks를 활용한 비동기 작업을 구현합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Background Tasks Skill

Celery, ARQ, FastAPI BackgroundTasks를 활용한 비동기 작업을 구현합니다.

## Triggers

- "백그라운드 태스크", "background task", "celery", "arq", "비동기 작업"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectPath` | ✅ | 프로젝트 경로 |
| `taskRunner` | ❌ | celery/arq/builtin (기본: celery) |

---

## Output

### 1. FastAPI Built-in BackgroundTasks (Simple)

```python
# app/api/v1/routes/notifications.py
from fastapi import APIRouter, BackgroundTasks

from app.application.services.email import send_email
from app.application.services.notification import process_notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/send-email")
async def send_welcome_email(
    email: str,
    background_tasks: BackgroundTasks,
):
    """Send email in background (simple tasks only)."""
    # Add task to background queue
    background_tasks.add_task(
        send_email,
        to=email,
        subject="Welcome!",
        body="Thanks for signing up.",
    )

    return {"message": "Email will be sent shortly"}


@router.post("/process")
async def create_notification(
    user_id: int,
    message: str,
    background_tasks: BackgroundTasks,
):
    """Process notification in background."""
    # Multiple background tasks
    background_tasks.add_task(process_notification, user_id, message)
    background_tasks.add_task(send_email, f"user-{user_id}@example.com", "New notification", message)

    return {"message": "Notification queued"}
```

### 2. Celery Setup (Production-Ready)

```python
# app/infrastructure/tasks/celery_app.py
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.infrastructure.tasks.tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes

    # Result settings
    result_expires=3600,  # 1 hour

    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Prefetch (1 = disable prefetching for long tasks)
    worker_prefetch_multiplier=1,

    # Concurrency
    worker_concurrency=4,

    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "app.infrastructure.tasks.tasks.cleanup_expired_tokens",
            "schedule": 3600.0,  # Every hour
        },
        "send-daily-reports": {
            "task": "app.infrastructure.tasks.tasks.send_daily_reports",
            "schedule": {
                "hour": 9,
                "minute": 0,
            },
        },
    },
)
```

### Celery Tasks

```python
# app/infrastructure/tasks/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

from app.application.services.email import EmailService
from app.application.services.report import ReportService

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_email_task(
    self,
    to: str,
    subject: str,
    body: str,
    template: str | None = None,
    context: dict | None = None,
) -> dict:
    """Send email asynchronously."""
    logger.info(f"Sending email to {to}: {subject}")

    try:
        # In Celery tasks, we need to create sync versions of our services
        # or use synchronous libraries
        import smtplib
        from email.mime.text import MIMEText

        from app.core.config import settings

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to}")
        return {"status": "sent", "to": to}

    except Exception as exc:
        logger.error(f"Failed to send email to {to}: {exc}")
        # Celery will auto-retry due to autoretry_for
        raise


@shared_task(bind=True, max_retries=3)
def process_order_task(self, order_id: int) -> dict:
    """Process order asynchronously."""
    logger.info(f"Processing order {order_id}")

    try:
        # Simulate order processing
        # In real implementation, import and use your order service
        import time
        time.sleep(5)  # Simulate processing

        return {"status": "processed", "order_id": order_id}

    except Exception as exc:
        logger.error(f"Failed to process order {order_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_tokens() -> dict:
    """Cleanup expired tokens (periodic task)."""
    logger.info("Running token cleanup")

    # In real implementation, connect to database and cleanup
    # Use synchronous database operations in Celery

    return {"status": "completed", "cleaned": 0}


@shared_task
def send_daily_reports() -> dict:
    """Send daily reports (scheduled task)."""
    logger.info("Generating daily reports")

    return {"status": "sent"}


@shared_task(bind=True)
def long_running_task(
    self,
    task_data: dict,
) -> dict:
    """Long running task with progress updates."""
    total_steps = task_data.get("steps", 100)

    for i in range(total_steps):
        # Update task state with progress
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total_steps,
                "percent": int((i + 1) / total_steps * 100),
            },
        )

        # Simulate work
        import time
        time.sleep(0.1)

    return {
        "status": "completed",
        "total_steps": total_steps,
    }
```

### Task Status API

```python
# app/api/v1/routes/tasks.py
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from app.infrastructure.tasks.celery_app import celery_app
from app.infrastructure.tasks.tasks import (
    long_running_task,
    process_order_task,
    send_email_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/send-email")
async def queue_send_email(
    to: str,
    subject: str,
    body: str,
):
    """Queue email sending task."""
    task = send_email_task.delay(to=to, subject=subject, body=body)

    return {
        "task_id": task.id,
        "status": "queued",
    }


@router.post("/process-order/{order_id}")
async def queue_process_order(order_id: int):
    """Queue order processing task."""
    task = process_order_task.delay(order_id=order_id)

    return {
        "task_id": task.id,
        "status": "queued",
    }


@router.post("/long-running")
async def queue_long_running(steps: int = 100):
    """Queue long running task."""
    task = long_running_task.delay(task_data={"steps": steps})

    return {
        "task_id": task.id,
        "status": "queued",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and result."""
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.status == "PROGRESS":
        response["progress"] = result.info
    elif result.status == "SUCCESS":
        response["result"] = result.result
    elif result.status == "FAILURE":
        response["error"] = str(result.result)

    return response


@router.delete("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a pending task."""
    celery_app.control.revoke(task_id, terminate=True)

    return {
        "task_id": task_id,
        "status": "cancelled",
    }
```

### 3. ARQ Setup (Async-Native)

```python
# app/infrastructure/tasks/arq_worker.py
from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings


async def get_arq_pool():
    """Get ARQ Redis pool."""
    return await create_pool(
        RedisSettings.from_dsn(settings.REDIS_URL)
    )


# ARQ worker settings
class WorkerSettings:
    """ARQ worker configuration."""

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

    # Job timeout
    job_timeout = 3600  # 1 hour

    # Max concurrent jobs
    max_jobs = 10

    # Functions to register
    functions = [
        "app.infrastructure.tasks.arq_tasks.send_email_async",
        "app.infrastructure.tasks.arq_tasks.process_data_async",
    ]

    # Cron jobs
    cron_jobs = [
        {
            "coroutine": "app.infrastructure.tasks.arq_tasks.daily_cleanup",
            "hour": 3,
            "minute": 0,
        },
    ]
```

### ARQ Tasks

```python
# app/infrastructure/tasks/arq_tasks.py
import asyncio

from arq import cron

import structlog

logger = structlog.get_logger()


async def send_email_async(
    ctx: dict,
    to: str,
    subject: str,
    body: str,
) -> dict:
    """Send email asynchronously with ARQ."""
    await logger.ainfo(f"Sending email to {to}")

    # Use async email library (e.g., aiosmtplib)
    import aiosmtplib
    from email.mime.text import MIMEText

    from app.core.config import settings

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )

    await logger.ainfo(f"Email sent to {to}")
    return {"status": "sent", "to": to}


async def process_data_async(
    ctx: dict,
    data_id: int,
    options: dict | None = None,
) -> dict:
    """Process data asynchronously."""
    await logger.ainfo(f"Processing data {data_id}")

    # Simulate async processing
    await asyncio.sleep(5)

    return {"status": "processed", "data_id": data_id}


@cron(hour=3, minute=0)
async def daily_cleanup(ctx: dict) -> dict:
    """Daily cleanup cron job."""
    await logger.ainfo("Running daily cleanup")

    # Cleanup logic here

    return {"status": "completed"}
```

### ARQ Task Dependency

```python
# app/api/v1/dependencies/tasks.py
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends

from app.infrastructure.tasks.arq_worker import get_arq_pool


async def get_task_queue() -> ArqRedis:
    """Get ARQ task queue dependency."""
    return await get_arq_pool()


TaskQueue = Annotated[ArqRedis, Depends(get_task_queue)]
```

### ARQ Routes

```python
# app/api/v1/routes/arq_tasks.py
from arq.jobs import Job
from fastapi import APIRouter, HTTPException

from app.api.v1.dependencies.tasks import TaskQueue

router = APIRouter(prefix="/arq-tasks", tags=["arq-tasks"])


@router.post("/send-email")
async def queue_email(
    to: str,
    subject: str,
    body: str,
    queue: TaskQueue,
):
    """Queue email with ARQ."""
    job = await queue.enqueue_job(
        "send_email_async",
        to=to,
        subject=subject,
        body=body,
    )

    return {
        "job_id": job.job_id,
        "status": "queued",
    }


@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    queue: TaskQueue,
):
    """Get ARQ job status."""
    job = Job(job_id, queue)
    info = await job.info()

    if not info:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": info.status,
        "result": info.result if info.status == "complete" else None,
    }
```

### Environment Settings

```python
# Add to app/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Email (for tasks)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@example.com"
```

## Running Workers

```bash
# Celery worker
celery -A app.infrastructure.tasks.celery_app worker --loglevel=info

# Celery beat (scheduler)
celery -A app.infrastructure.tasks.celery_app beat --loglevel=info

# Celery flower (monitoring)
celery -A app.infrastructure.tasks.celery_app flower

# ARQ worker
arq app.infrastructure.tasks.arq_worker.WorkerSettings
```

## Task Selection Guide

| Use Case | Recommended |
|----------|-------------|
| Simple, quick tasks | FastAPI BackgroundTasks |
| Production workloads | Celery |
| Async-native, Python 3.11+ | ARQ |
| Scheduled tasks | Celery Beat / ARQ Cron |
| Task monitoring | Celery Flower |

## References

- `_references/ARCHITECTURE-PATTERN.md`
