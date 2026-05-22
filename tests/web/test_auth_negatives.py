import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.auth, pytest.mark.regression]


@allure.feature("Auth")
@allure.story("Login invalido")
def test_invalid_login(page: Page, settings: Settings, browser_name: str) -> None:
    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/login",
                "Usuario utilizado: qa-invalid@example.com",
                f"Browser: {browser_name}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )

    with allure.step("Login invalido rechazado"):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("qa-invalid@example.com", "Wrong1234")
        login_page.expect_invalid_login()
        step_log("Login invalido rechazado")
        attach_final_screenshot(page, "invalid-login-final")
