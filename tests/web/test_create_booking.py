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


pytestmark = [pytest.mark.web, pytest.mark.booking, pytest.mark.smoke]


@allure.feature("Reservas")
@allure.story("Crear reserva simple")
def test_create_simple_booking_smoke(
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

    with allure.step("Login exitoso"):
        LoginPage(page).open()
        LoginPage(page).login(user["email"], user["password"])
        LoginPage(page).expect_logged_in()
        step_log("Login exitoso")
        attach_final_screenshot(page, "login-home-final")

    with allure.step("Reserva creada correctamente"):
        bookings_page = BookingsPage(page)
        try:
            bookings_page.open()
            bookings_page.create_simple_booking(booking["customer_search"], booking["customer_name"], booking["court_name"])
            bookings_page.expect_booking_visible(booking["customer_name"])
            step_log("Reserva creada correctamente")
            attach_final_screenshot(page, "booking-created-final")
        finally:
            qa_client.reset_customer(booking["customer_clean_id"])
