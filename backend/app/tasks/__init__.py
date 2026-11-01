from app.tasks.auction import process_auction_ticks
from app.tasks.celery_app import celery_app

__all__ = ["celery_app", "process_auction_ticks"]
