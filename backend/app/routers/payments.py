from datetime import datetime, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.ticket import Ticket
from app.models.user import User


router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentCreate(BaseModel):
    reservation_id: int
    payment_id: str
    success: bool = True


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Блокуємо бронювання під час обробки платежу.
        reservation = (
            db.query(Reservation)
            .filter(Reservation.id == data.reservation_id)
            .with_for_update()
            .first()
        )

        if not reservation:
            raise HTTPException(
                status_code=404,
                detail="Reservation not found"
            )

        if reservation.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="This reservation belongs to another user"
            )

        # Перевіряємо, чи цей платіж уже оброблявся.
        existing_payment = (
            db.query(Payment)
            .filter(Payment.payment_id == data.payment_id)
            .first()
        )

        if existing_payment:
            if existing_payment.reservation_id != reservation.id:
                raise HTTPException(
                    status_code=409,
                    detail="Payment ID belongs to another reservation"
                )

            return {
                "payment_id": existing_payment.payment_id,
                "status": existing_payment.status,
                "reservation_status": reservation.status
            }

        if reservation.status == "paid":
            raise HTTPException(
                status_code=409,
                detail="Reservation already paid"
            )

        now = datetime.now(timezone.utc)

        if reservation.status != "reserved" or reservation.expires_at <= now:
            raise HTTPException(
                status_code=400,
                detail="Reservation is not active"
            )

        # Створюємо запис про платіж.
        payment = Payment(
            reservation_id=reservation.id,
            payment_id=data.payment_id,
            status="paid" if data.success else "failed"
        )

        db.add(payment)

        # Якщо оплата успішна, підтверджуємо бронювання.
        if data.success:
            reservation.status = "paid"

            # Створюємо електронний квиток.
            ticket = Ticket(
                reservation_id=reservation.id,
                qr_code=secrets.token_urlsafe(32)
            )

            db.add(ticket)

        # Зберігаємо зміни в базі даних.
        db.commit()

        return {
            "payment_id": payment.payment_id,
            "status": payment.status,
            "reservation_status": reservation.status
        }

    except Exception:
        db.rollback()
        raise