import asyncio
from datetime import datetime, timezone

from sqlalchemy import update

from app.database import SessionLocal
from app.models.reservation import Reservation


def expire_reservations():
    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        result = db.execute(
            update(Reservation)
            .where(
                Reservation.status == "reserved",
                Reservation.expires_at <= now
            )
            .values(status="expired")
        )

        db.commit()

        if result.rowcount:
            print(f"Expired reservations: {result.rowcount}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


async def reservation_worker():
    while True:
        try:
            await asyncio.to_thread(expire_reservations)
        except Exception as error:
            print(f"Reservation worker error: {error}")

        await asyncio.sleep(30)