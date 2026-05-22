import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from api.qa_client import QaClient
from pages.bookings_page import BookingsPage
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_data_guards import require_controlled_booking_customer, require_web_booking_create_enabled
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.booking, pytest.mark.regression]


def _attach_test_data(settings: Settings, user: dict, booking: dict, browser_name: str) -> None:
    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/bookings",
                f"Usuario utilizado: {user['email']}",
                f"Cliente: {booking['customer_name']}",
                f"Browser: {browser_name}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )


def _login(page: Page, user: dict) -> None:
    LoginPage(page).open()
    LoginPage(page).login(user["email"], user["password"])
    LoginPage(page).expect_logged_in()
    step_log("Login exitoso")


@allure.feature("Reservas")
@allure.story("Slot ocupado bloquea reserva duplicada")
def test_create_booking_occupied_slot(
    page: Page,
    web_users: dict,
    web_booking: dict,
    settings: Settings,
    browser_name: str,
    qa_client: QaClient,
) -> None:
    user = web_users["users"]["super_admin"]
    booking = web_booking["booking"]
    require_controlled_booking_customer(booking)
    require_web_booking_create_enabled(booking)
    qa_client.reset_customer(booking["customer_clean_id"])
    _attach_test_data(settings, user, booking, browser_name)

    with allure.step("Login exitoso"):
        _login(page, user)

    bookings_page = BookingsPage(page)
    booking_slot = None

    try:
        with allure.step("Reserva creada"):
            bookings_page.open()
            booking_slot = bookings_page.create_booking(
                booking["customer_search"], booking["customer_name"], booking["court_name"]
            )
            bookings_page.expect_booking_visible(booking["customer_name"])
            step_log("Reserva creada")

        with allure.step("Reserva duplicada bloqueada"):
            bookings_page.expect_slot_occupied(booking_slot)
            step_log("Reserva duplicada bloqueada")
            attach_final_screenshot(page, "booking-occupied-slot-final")
    finally:
        if booking_slot:
            bookings_page.close_new_booking_modal()
            bookings_page.open_booking_details_by_slot(booking_slot, booking["customer_name"])
            bookings_page.cancel_open_booking()
        qa_client.reset_customer(booking["customer_clean_id"])


@allure.feature("Reservas")
@allure.story("No-show futuro bloqueado")
def test_no_show_future_blocked(
    page: Page,
    web_users: dict,
    web_booking: dict,
    settings: Settings,
    browser_name: str,
    qa_client: QaClient,
) -> None:
    user = web_users["users"]["super_admin"]
    booking = web_booking["booking"]
    require_controlled_booking_customer(booking)
    require_web_booking_create_enabled(booking)
    qa_client.reset_customer(booking["customer_clean_id"])
    _attach_test_data(settings, user, booking, browser_name)

    with allure.step("Login exitoso"):
        _login(page, user)

    bookings_page = BookingsPage(page)
    booking_slot = None

    try:
        with allure.step("Reserva futura creada"):
            bookings_page.open()
            booking_slot = bookings_page.create_booking(
                booking["customer_search"], booking["customer_name"], booking["court_name"]
            )
            bookings_page.open_booking_details_by_slot(booking_slot, booking["customer_name"])
            step_log("Reserva futura creada")

        with allure.step("No-show futuro bloqueado"):
            bookings_page.attempt_no_show()
            bookings_page.expect_no_show_future_blocked()
            step_log("No-show futuro bloqueado")
            attach_final_screenshot(page, "no-show-future-blocked-final")
    finally:
        if booking_slot:
            bookings_page.cancel_open_booking()
        qa_client.reset_customer(booking["customer_clean_id"])
