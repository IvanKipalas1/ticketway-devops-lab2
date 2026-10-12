from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models.event import Event
from app.models.user import User
from app.dependencies import get_current_user


def test_reservation_requires_auth(client):
    response = client.post(
        "/reservations/",
        json={
            "event_id": 1,
            "seat_number": 10
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_double_reservation(client, db_session):
    # Створюємо тестового користувача
    user = User(
        email="reservation_test@example.com",
        hashed_password="test_hash",
        is_admin=False
    )

    # Створюємо тестову подію
    event = Event(
        title="Test Concert",
        description="Test event",
        location="Kyiv",
        event_date=datetime.now(timezone.utc) + timedelta(days=30),
        price=500,
        total_seats=100
    )

    db_session.add_all([user, event])
    db_session.commit()

    db_session.refresh(user)
    db_session.refresh(event)

    # Імітуємо авторизованого користувача
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        data = {
            "event_id": event.id,
            "seat_number": 25
        }

        # Перше бронювання
        response1 = client.post(
            "/reservations/",
            json=data
        )

        assert response1.status_code == 201
        assert response1.json()["status"] == "reserved"

        # Повторне бронювання того самого місця
        response2 = client.post(
            "/reservations/",
            json=data
        )

        assert response2.status_code == 409
        assert response2.json()["detail"] == "Seat is already reserved"

    finally:
        app.dependency_overrides.pop(get_current_user, None)