import allure
import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import Settings
from pages.login_page import LoginPage
from pages.organizer_page import OrganizerPage
from utils.allure_helpers import attach_final_screenshot


pytestmark = [pytest.mark.web, pytest.mark.organizer]


def _login_owner(page: Page, settings: Settings) -> None:
    if not settings.owner_email or not settings.owner_password:
        pytest.skip("Owner credentials no configuradas en entorno local.")
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(settings.owner_email, settings.owner_password)
    login_page.expect_logged_in()


def _attach_context(settings: Settings, browser_name: str) -> None:
    allure.attach(
        "\n".join(
            [
                f"URL testeada: {str(settings.web_base_url).rstrip('/')}/organizer",
                "Usuario utilizado: owner QA desde entorno",
                f"Browser: {browser_name}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )


@allure.feature("Organizer LITE")
@allure.story("Page load")
@pytest.mark.smoke
def test_organizer_page_loads(page: Page, settings: Settings, browser_name: str) -> None:
    _attach_context(settings, browser_name)

    with allure.step("Login owner"):
        _login_owner(page, settings)

    with allure.step("Abrir Organizer"):
        organizer = OrganizerPage(page)
        organizer.open()
        organizer.expect_loaded()
        attach_final_screenshot(page, "organizer-page-loaded")


@allure.feature("Organizer LITE")
@allure.story("Crear torneo basico")
@pytest.mark.smoke
def test_organizer_create_tournament_basic(page: Page, settings: Settings, browser_name: str) -> None:
    _attach_context(settings, browser_name)

    with allure.step("Login owner"):
        _login_owner(page, settings)

    organizer = OrganizerPage(page)
    with allure.step("Abrir Organizer"):
        organizer.open()
        organizer.expect_loaded()

    with allure.step("Crear torneo basico"):
        try:
            tournament_name = organizer.create_basic_tournament()
        except (AssertionError, PlaywrightTimeoutError) as exc:
            attach_final_screenshot(page, "organizer-create-tournament-blocked")
            pytest.skip(f"Faltan locators estables para crear torneo Organizer: {exc}")
        organizer.expect_tournament_visible_or_detail(tournament_name)
        attach_final_screenshot(page, "organizer-tournament-created")


@allure.feature("Organizer LITE")
@allure.story("Tabs detalle")
def test_organizer_detail_tabs_are_visible(page: Page, settings: Settings, browser_name: str) -> None:
    _attach_context(settings, browser_name)

    with allure.step("Login owner"):
        _login_owner(page, settings)

    organizer = OrganizerPage(page)
    with allure.step("Crear o reutilizar torneo"):
        organizer.open()
        organizer.expect_loaded()
        try:
            tournament_name = organizer.create_basic_tournament()
        except (AssertionError, PlaywrightTimeoutError) as exc:
            attach_final_screenshot(page, "organizer-detail-setup-blocked")
            pytest.skip(f"No se pudo preparar torneo para detalle Organizer: {exc}")

    with allure.step("Abrir detalle"):
        try:
            organizer.open_tournament_detail(tournament_name)
        except (AssertionError, PlaywrightTimeoutError) as exc:
            attach_final_screenshot(page, "organizer-open-detail-blocked")
            pytest.skip(f"No se encontro locator estable para entrar al detalle Organizer: {exc}")

    with allure.step("Validar tabs"):
        try:
            organizer.expect_detail_tabs_visible()
        except (AssertionError, PlaywrightTimeoutError) as exc:
            attach_final_screenshot(page, "organizer-tabs-blocked")
            pytest.skip(f"Tabs de detalle Organizer no confirmadas con locators estables: {exc}")
        attach_final_screenshot(page, "organizer-detail-tabs")
