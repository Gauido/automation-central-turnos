import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.bookings_page import BookingsPage
from pages.login_page import LoginPage
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
) -> None:
    user = web_users["users"]["super_admin"]
    booking = web_booking["booking"]

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
        allure.attach(
            page.screenshot(full_page=True),
            name="post-login-home",
            attachment_type=allure.attachment_type.PNG,
        )

    with allure.step("Reserva creada correctamente"):
        bookings_page = BookingsPage(page)
        bookings_page.open()
        bookings_page.create_simple_booking(booking["customer_search"], booking["customer_name"])
        bookings_page.expect_booking_visible(booking["customer_name"])
        step_log("Reserva creada correctamente")
        allure.attach(
            page.screenshot(full_page=True),
            name="booking-created-final",
            attachment_type=allure.attachment_type.PNG,
        )
