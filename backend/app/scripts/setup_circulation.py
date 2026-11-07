import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import select

_BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.core.database import async_session_maker
from app.models.enums import LotStatus
from app.models.lot import Lot


async def run_setup() -> None:
    async with async_session_maker() as session:
        result = await session.execute(select(Lot).order_by(Lot.created_at.asc()))
        lots = list(result.scalars().all())
        if len(lots) < 14:
            return

        now = datetime.now(UTC)
        for lot in lots[:6]:
            lot.status = LotStatus.ACTIVE
            lot.current_price = lot.start_price
            lot.started_at = now
            lot.next_drop_at = now + timedelta(seconds=lot.interval_seconds)
            lot.updated_at = now

        for idx, lot in enumerate(lots[6:14]):
            lot.status = LotStatus.EXPIRED
            lot.current_price = lot.floor_price
            lot.updated_at = now - timedelta(minutes=(8 - idx) * 10)

        for lot in lots[14:]:
            lot.status = LotStatus.DRAFT
            lot.current_price = lot.start_price
            lot.started_at = None
            lot.next_drop_at = None
            lot.taken_at = None
            lot.winner_id = None
            lot.final_price = None
            lot.updated_at = now - timedelta(hours=2)

        await session.commit()

        for st in LotStatus:
            count_res = await session.execute(select(Lot).where(Lot.status == st))
            found = list(count_res.scalars().all())
            print(f"{st.value}: {len(found)}")


if __name__ == "__main__":
    asyncio.run(run_setup())
