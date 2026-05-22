import allure
import pytest
from playwright.sync_api import Browser

from config.settings import Settings
from api.qa_client import QaClient
from pages.bookings_page import BookingsPage
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_data_guards import require_controlled_booking_customer, require_web_booking_create_enabled
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.booking, pytest.mark.regression]


def _login(page, user: dict) -> None:
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(user["email"], user["password"])
    login_page.expect_logged_in()


@allure.feature("Reservas")
@allure.story("Concurrencia simple mismo slot")
def test_booking_race_condition(
    browser: Browser,
    browser_context_args: dict,
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

    context_a = browser.new_context(**browser_context_args)
    context_b = browser.new_context(**browser_context_args)
    page_a = context_a.new_page()
    page_b = context_b.new_page()
    booking_slot = None

    try:
        with allure.step("Usuarios logueados"):
            _login(page_a, user)
            _login(page_b, user)
            step_log("Usuarios logueados")

        page_a_model = BookingsPage(page_a)
        page_b_model = BookingsPage(page_b)

        with allure.step("Mismo slot seleccionado"):
            page_a_model.open()
            page_b_model.open()
            slot_a = page_a_model.start_booking_for_first_available_slot(
                booking["customer_search"], booking["customer_name"], booking["court_name"]
            )
            slot_b = page_b_model.start_booking_for_first_available_slot(
                booking["customer_search"], booking["customer_name"], booking["court_name"]
            )
            assert slot_a == slot_b
            booking_slot = slot_a
            step_log("Mismo slot seleccionado")

        with allure.step("Una reserva gana y la otra queda bloqueada"):
            page_a_model.submit_booking()
            page_a_model.expect_booking_visible(booking["customer_name"])
            page_b_model.submit_booking()
            page_b_model.expect_booking_create_blocked()
            step_log("Una reserva gana y la otra queda bloqueada")
            attach_final_screenshot(page_b, "booking-race-condition-final")
    finally:
        if booking_slot:
            page_a_model.open_booking_details_by_slot(booking_slot, booking["customer_name"])
            page_a_model.cancel_open_booking()
        qa_client.reset_customer(booking["customer_clean_id"])
        context_a.close()
        context_b.close()
