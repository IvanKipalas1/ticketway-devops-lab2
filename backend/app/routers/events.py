from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.event import Event
from app.models.user import User
from app.dependencies import require_admin
router = APIRouter(prefix="/events", tags=["Events"])


class EventCreate(BaseModel):
    title: str
    description: str
    location: str
    event_date: datetime
    price: float
    total_seats: int


@router.post("/")
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    new_event = Event(**event.model_dump())

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event


@router.get("/")
def get_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event