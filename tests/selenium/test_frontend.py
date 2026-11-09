import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

URL = "http://localhost:8080"


def create_driver():
    options = Options()

    if os.getenv("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=options)

def test_ticketway_page():
    driver = create_driver()

    try:
        driver.get(URL)

        assert "TicketWay" in driver.title

        heading = driver.find_element(By.TAG_NAME, "h1")
        assert heading.text == "TicketWay"

        buttons = driver.find_elements(By.TAG_NAME, "button")
        button_names = [button.text for button in buttons]

        assert "Зареєструватися" in button_names
        assert "Увійти" in button_names

    finally:
        driver.quit()


import uuid
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_user_registration():
    driver = create_driver()

    try:
        driver.get(URL)

        email = f"test_{uuid.uuid4().hex[:12]}@example.com"

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys("TestPassword123!")

        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Зареєструватися')]"
        ).click()

        message = WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message"),
                "Реєстрація успішна"
            )
        )

        assert message

    finally:
        driver.quit()


def test_user_login():
    driver = create_driver()

    try:
        driver.get(URL)

        email = f"login_{uuid.uuid4().hex[:12]}@example.com"
        password = "TestPassword123!"

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)

        # Реєструємо нового користувача
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Зареєструватися')]"
        ).click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "message"), "Реєстрація успішна"
            )
        )

        # Виконуємо вхід
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Увійти')]"
        ).click()

        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.ID, "authStatus"), "Ви авторизовані"
            )
        )

        assert driver.find_element(
            By.ID, "authStatus"
        ).text == "Ви авторизовані"

    finally:
        driver.quit()


def test_seat_reservation():
    driver = create_driver()

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 10)

        email = f"booking_{uuid.uuid4().hex[:12]}@example.com"
        password = "TestPassword123!"

        # Реєстрація
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Зареєструватися')]"
        ).click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "message"), "Реєстрація успішна"
        ))

        # Авторизація
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Увійти')]"
        ).click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "authStatus"), "Ви авторизовані"
        ))

        # Вибір події
        driver.find_element(By.ID, "eventId").send_keys("1")

        # Вибираємо випадкове місце
        import random
        seat = random.randint(200, 500)

        driver.find_element(By.ID, "seat").send_keys(str(seat))

        # Бронювання
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Забронювати місце')]"
        ).click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "message"), "Місце успішно заброньовано"
        ))

        assert "Бронювання №" in driver.find_element(
            By.ID, "reservationInfo"
        ).text

    finally:
        driver.quit()


def test_double_reservation():
    driver = create_driver()

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 10)

        email = f"double_{uuid.uuid4().hex[:12]}@example.com"
        password = "TestPassword123!"

        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)

        # Реєстрація
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Зареєструватися')]"
        ).click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "message"), "Реєстрація успішна"
        ))

        # Вхід
        driver.find_element(
            By.XPATH, "//button[contains(text(), 'Увійти')]"
        ).click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "authStatus"), "Ви авторизовані"
        ))

        # Знаходимо вільне місце для тесту
        import random
        seat = random.randint(1, 500)

        driver.find_element(By.ID, "eventId").send_keys("1")
        driver.find_element(By.ID, "seat").send_keys(str(seat))

        reserve_button = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Забронювати місце')]"
        )

        # Перше бронювання
        reserve_button.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "message"), "Місце успішно заброньовано"
        ))

        # Повторне бронювання того самого місця
        reserve_button.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.ID, "message"), "Seat is already reserved"
        ))

        assert "Seat is already reserved" in driver.find_element(
            By.ID, "message"
        ).text

    finally:
        driver.quit()
