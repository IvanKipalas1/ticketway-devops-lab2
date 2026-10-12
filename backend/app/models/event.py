from sqlalchemy import Column, Integer, String, DateTime, Float
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    location = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)