import allure
import pytest
from playwright.sync_api import Page, expect

from config.settings import Settings
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_data_guards import require_user
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.roles, pytest.mark.regression]


@allure.feature("Roles")
@allure.story("Permisos staff basicos")
def test_staff_permissions_basic(page: Page, web_users: dict, settings: Settings, browser_name: str) -> None:
    staff = web_users["users"]["staff"]
    require_user(staff, "staff")

    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}",
                f"Usuario utilizado: {staff['email']}",
                f"Browser: {browser_name}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )

    with allure.step("Login staff exitoso"):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(staff["email"], staff["password"])
        login_page.expect_logged_in()
        step_log("Login staff exitoso")

    with allure.step("Acciones owner criticas no visibles"):
        page.goto("/subscription")
        expect(page.get_by_text("Suscripción", exact=False)).not_to_be_visible(timeout=5000)
        page.goto("/users")
        expect(page.get_by_role("button", name="Eliminar")).not_to_be_visible(timeout=5000)
        step_log("Acciones owner criticas no visibles")
        attach_final_screenshot(page, "staff-permissions-basic-final")
