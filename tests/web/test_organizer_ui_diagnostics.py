from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.login_page import LoginPage
from pages.organizer_page import OrganizerPage
from utils.dom_discovery import discover_dom


pytestmark = [pytest.mark.web, pytest.mark.organizer, pytest.mark.diagnostics, pytest.mark.debug]


def _login_owner(page: Page, settings: Settings) -> None:
    if not settings.owner_email or not settings.owner_password:
        pytest.skip("Owner credentials no configuradas en entorno local.")
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(settings.owner_email, settings.owner_password)
    login_page.expect_logged_in()


def _assert_discovery_artifacts(result: dict) -> None:
    assert result["visibleText"], "La pantalla no debe estar vacia."
    assert result["counts"]["headings"] > 0 or result["visibleText"], "Debe existir heading o texto principal."
    for artifact in result["artifacts"].values():
        assert Path(artifact).exists(), f"No se genero artifact: {artifact}"


@allure.feature("Organizer LITE")
@allure.story("UI diagnostics lista")
def test_organizer_list_ui_diagnostics(page: Page, settings: Settings) -> None:
    with allure.step("Login owner"):
        _login_owner(page, settings)

    organizer = OrganizerPage(page)
    with allure.step("Abrir Organizer"):
        organizer.open()
        organizer.expect_loaded()

    with allure.step("Extraer DOM de lista Organizer"):
        result = discover_dom(page, "organizer-list")
        _assert_discovery_artifacts(result)
        assert result["counts"]["buttons"] > 0 or result["counts"]["links"] > 0


@allure.feature("Organizer LITE")
@allure.story("UI diagnostics modal crear torneo")
def test_organizer_create_tournament_modal_ui_diagnostics(page: Page, settings: Settings) -> None:
    with allure.step("Login owner"):
        _login_owner(page, settings)

    organizer = OrganizerPage(page)
    with allure.step("Abrir modal Nuevo torneo"):
        organizer.open()
        organizer.expect_loaded()
        organizer.open_create_tournament()

    with allure.step("Extraer DOM del modal"):
        result = discover_dom(page, "organizer-create-modal", root_selector='[role="dialog"]')
        _assert_discovery_artifacts(result)
        assert result["counts"]["inputs"] > 0
        assert result["counts"]["buttons"] > 0


@allure.feature("Organizer LITE")
@allure.story("UI diagnostics detalle")
def test_organizer_detail_ui_diagnostics(page: Page, settings: Settings) -> None:
    with allure.step("Login owner"):
        _login_owner(page, settings)

    organizer = OrganizerPage(page)
    with allure.step("Crear torneo y abrir detalle"):
        organizer.open()
        organizer.expect_loaded()
        tournament_name = organizer.create_basic_tournament()
        organizer.open_tournament_detail(tournament_name)

    with allure.step("Extraer DOM del detalle Organizer"):
        result = discover_dom(page, "organizer-detail")
        _assert_discovery_artifacts(result)
        assert result["counts"]["tabs"] > 0 or "Categorias" in result["visibleText"] or "Categor" in result["visibleText"]
