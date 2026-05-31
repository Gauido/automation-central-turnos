import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.bookings_page import BookingsPage
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.booking, pytest.mark.smoke]


@allure.feature("Reservas")
@allure.story("Ver detalle desde acciones")
def test_view_booking_from_grid_actions(page: Page, web_users: dict, settings: Settings, browser_name: str) -> None:
    user = web_users["users"]["super_admin"]

    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/bookings",
                f"Usuario utilizado: {user['email']}",
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

    with allure.step("Detalle de reserva visible"):
        bookings_page = BookingsPage(page)
        bookings_page.open()
        if not bookings_page.has_visible_bookings():
            pytest.skip(
                "No hay reservas visibles para abrir acciones; bloqueado por data/setup hasta resolver POST /api/bookings"
            )
        bookings_page.open_first_booking_details()
        bookings_page.expect_booking_details()
        step_log("Detalle de reserva visible")
        attach_final_screenshot(page, "booking-detail-final")
