import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
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

    login_page = LoginPage(page)
    step_log("abrir login")
    login_page.open()
    step_log("enviar credenciales")
    login_page.login(user["email"], user["password"])
    login_page.expect_logged_in()
    ok_log("login exitoso")
    allure.attach(
        page.screenshot(full_page=True),
        name="login-home-final",
        attachment_type=allure.attachment_type.PNG,
    )
