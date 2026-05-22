from datetime import datetime

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.courts_page import CourtsPage
from pages.login_page import LoginPage
from utils.allure_helpers import attach_final_screenshot
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.court, pytest.mark.smoke]


@allure.feature("Canchas")
@allure.story("Crear cancha")
def test_create_court(page: Page, web_users: dict, web_courts: dict, settings: Settings, browser_name: str) -> None:
    user = web_users["users"]["super_admin"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    court_name = f"{web_courts['court']['name_prefix']}_{timestamp}"
    court_number = 20 + (int(timestamp[-4:]) % 80)

    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/courts",
                f"Usuario utilizado: {user['email']}",
                f"Cancha: {court_name}",
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

    with allure.step("Cancha creada correctamente"):
        courts_page = CourtsPage(page)
        courts_page.open()
        try:
            courts_page.create_court(court_name, number=court_number)
            courts_page.expect_court_visible(court_name)
            step_log("Cancha creada correctamente")
            attach_final_screenshot(page, "court-created-final")
        finally:
            courts_page.delete_court_by_name(court_name)
            courts_page.expect_court_not_visible(court_name)
            attach_final_screenshot(page, "court-deleted-final")
