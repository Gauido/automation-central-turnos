import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_logger import log_test, ok_log, step_log


pytestmark = [pytest.mark.web, pytest.mark.auth, pytest.mark.smoke]


@allure.feature("Auth")
@allure.story("Login web super admin")
@pytest.mark.web_login
def test_web_login_super_admin(page: Page, web_users: dict, settings: Settings, browser_name: str) -> None:
    log_test("web login super admin")
    user = web_users["users"]["super_admin"]

    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/login",
                f"Usuario utilizado: {user['email']}",
                f"Browser: {browser_name}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )

    with allure.step("Login exitoso"):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(user["email"], user["password"])
        login_page.expect_logged_in()
        step_log("Login exitoso")
        ok_log("login exitoso")
        attach_final_screenshot(page, "login-home-final")
