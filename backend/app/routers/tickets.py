from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ticket import Ticket
from app.models.reservation import Reservation
from app.models.user import User


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/{ticket_id}/qr")
def get_ticket_qr(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Шукаємо квиток у базі даних.
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Перевіряємо, кому належить квиток.
    reservation = (
        db.query(Reservation)
        .filter(Reservation.id == ticket.reservation_id)
        .first()
    )

    if not reservation or reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    # QR-код доступний тільки для оплаченого квитка.
    if reservation.status != "paid":
        raise HTTPException(
            status_code=400,
            detail="Ticket is not paid"
        )

    # Генеруємо QR-код.
    qr_image = qrcode.make(ticket.qr_code)

    # Зберігаємо зображення в оперативній пам'яті.
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    # Повертаємо PNG-зображення.
    return StreamingResponse(
        image_buffer,
        media_type="image/png"
    )