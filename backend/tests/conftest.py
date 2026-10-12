import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.event import Event
from app.models.user import User
from app.models.reservation import Reservation
from app.models.payment import Payment
from app.models.ticket import Ticket


TEST_DATABASE_URL = (
    "postgresql+psycopg2://postgres:secret@localhost:5433/ticketway_test"
)

# Захист від випадкового використання основної бази
assert TEST_DATABASE_URL.endswith("/ticketway_test")

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture
def db_session():
    # Створюємо таблиці в тестовій базі
    Base.metadata.create_all(bind=test_engine)

    # Очищаємо тестові таблиці перед тестом
    with test_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()

        # Очищаємо тестові таблиці після тесту
        with test_engine.begin() as connection:
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()