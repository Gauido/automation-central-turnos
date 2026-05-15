from datetime import datetime

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.courts_page import CourtsPage
from pages.login_page import LoginPage
from utils.test_logger import step_log


pytestmark = [pytest.mark.web, pytest.mark.court, pytest.mark.smoke]


@allure.feature("Canchas")
@allure.story("Crear cancha")
def test_create_court(page: Page, web_users: dict, web_courts: dict, settings: Settings, browser_name: str) -> None:
    user = web_users["users"]["super_admin"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    court_name = f"{web_courts['court']['name_prefix']}_{timestamp}"
    court_number = int(timestamp[-6:])

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
            page.wait_for_timeout(1000)
            step_log("Cancha creada correctamente")
            allure.attach(
                page.screenshot(full_page=True),
                name="court-created-final",
                attachment_type=allure.attachment_type.PNG,
            )
        finally:
            courts_page.delete_court_by_name(court_name)
            courts_page.expect_court_not_visible(court_name)
            page.wait_for_timeout(1000)
            allure.attach(
                page.screenshot(full_page=True),
                name="court-deleted-final",
                attachment_type=allure.attachment_type.PNG,
            )
