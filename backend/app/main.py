import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine

from app.models.event import Event
from app.models.user import User
from app.models.reservation import Reservation
from app.models.payment import Payment
from app.models.ticket import Ticket

from app.routers.events import router as events_router
from app.routers.auth import router as auth_router
from app.routers.reservations import router as reservations_router
from app.routers.payments import router as payments_router
from app.routers.tickets import router as tickets_router

from app.services.reservation_worker import reservation_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(reservation_worker())

    try:
        yield
    finally:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="TicketWay API",
    description="API для системи бронювання квитків",
    version="1.0.0",
    lifespan=lifespan
)


Base.metadata.create_all(bind=engine)


app.include_router(events_router)
app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(payments_router)
app.include_router(tickets_router)


@app.get("/")
def home():
    return {"message": "Welcome to TicketWay API"}


@app.get("/health")
def health():
    return {"status": "healthy"}