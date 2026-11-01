from collections.abc import Callable
from typing import Any, TypeVar, cast

from app.tasks.celery_app import celery_app

F = TypeVar("F", bound=Callable[..., Any])


def task(*args: Any, **kwargs: Any) -> Callable[[F], F]:
    return cast(Callable[[F], F], celery_app.task(*args, **kwargs))


@task(name="app.tasks.auction.process_auction_ticks")
def process_auction_ticks() -> dict[str, int]:
    return {"ticks_processed": 0, "expired_processed": 0}
