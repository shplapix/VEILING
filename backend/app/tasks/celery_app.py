from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "archive_auction",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.auction"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_pool="solo",
    beat_schedule={
        "process-auction-ticks-every-5s": {
            "task": "app.tasks.auction.process_auction_ticks",
            "schedule": 5.0,
        },
        "cycle-auction-lots-every-5s": {
            "task": "app.tasks.auction.cycle_auction_lots",
            "schedule": 5.0,
        },
    },
)
