from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.event import Event
from app.models.reservation import Reservation
from app.models.user import User


router = APIRouter(prefix="/reservations", tags=["Reservations"])


class ReservationCreate(BaseModel):
    event_id: int
    seat_number: int = Field(gt=0)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Блокуємо подію на час перевірки та створення бронювання.
        # Це не дозволить двом запитам одночасно зайняти одне місце.
        event = (
            db.query(Event)
            .filter(Event.id == data.event_id)
            .with_for_update()
            .first()
        )

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        if data.seat_number > event.total_seats:
            raise HTTPException(
                status_code=400,
                detail="Invalid seat number"
            )

        now = datetime.now(timezone.utc)

        # Перевіряємо, чи місце вже зайняте.
        existing_reservation = (
            db.query(Reservation)
            .filter(
                Reservation.event_id == data.event_id,
                Reservation.seat_number == data.seat_number,
                (
                    (Reservation.status == "paid")
                    | (
                        (Reservation.status == "reserved")
                        & (Reservation.expires_at > now)
                    )
                )
            )
            .first()
        )

        if existing_reservation:
            raise HTTPException(
                status_code=409,
                detail="Seat is already reserved"
            )

        # Позначаємо прострочені бронювання як expired.
        expired_reservations = (
            db.query(Reservation)
            .filter(
                Reservation.event_id == data.event_id,
                Reservation.seat_number == data.seat_number,
                Reservation.status == "reserved",
                Reservation.expires_at <= now
            )
            .all()
        )

        for reservation in expired_reservations:
            reservation.status = "expired"

        new_reservation = Reservation(
            user_id=current_user.id,
            event_id=data.event_id,
            seat_number=data.seat_number,
            status="reserved",
            expires_at=now + timedelta(minutes=10)
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)

        return {
            "id": new_reservation.id,
            "event_id": new_reservation.event_id,
            "seat_number": new_reservation.seat_number,
            "status": new_reservation.status,
            "expires_at": new_reservation.expires_at
        }

    except Exception:
        db.rollback()
        raise