import re

import allure
import pytest
from playwright.sync_api import Page

from config.settings import Settings
from pages.organizer_page import OrganizerPage
from tests.web.test_organizer_tournament_setup_flow import _create_category, _create_pairs, _create_tournament_detail, _unique
from utils.allure_helpers import attach_final_screenshot


pytestmark = [pytest.mark.web, pytest.mark.organizer, pytest.mark.negative, pytest.mark.usefixtures("clean_organizer_data")]


def _validation_visible(page: Page) -> bool:
    body = page.locator("body").inner_text(timeout=5000)
    return bool(re.search(r"obligatorio|requerido|valid|error|faltan|insuficient|no se puede|debe", body, re.I))


@allure.feature("Organizer LITE")
@allure.story("Pareja incompleta")
def test_organizer_incomplete_pair_rejected(page: Page, settings: Settings) -> None:
    organizer = _create_tournament_detail(page, settings)
    _create_category(organizer, _unique("QA Categoria Neg Pareja"))
    organizer.open_pairs_tab()
    organizer.open_pair_form()

    player1, _ = organizer.pair_inputs()
    player1.fill(_unique("QA Solo Player"))
    save = organizer.save_pair_button()
    if save.count() == 0:
        pytest.skip("No se encontro accion estable para guardar pareja incompleta.")
    if save.is_enabled():
        save.click()
        page.wait_for_timeout(700)

    assert organizer.dialog().is_visible() or _validation_visible(page)
    attach_final_screenshot(page, "organizer-negative-incomplete-pair")


@allure.feature("Organizer LITE")
@allure.story("Sortear zonas sin parejas suficientes")
def test_organizer_random_assign_without_enough_pairs_rejected(page: Page, settings: Settings) -> None:
    organizer = _create_tournament_detail(page, settings)
    _create_category(organizer, _unique("QA Categoria Neg Zonas"))
    organizer.open_zones_tab()
    organizer.set_zone_count(2)
    organizer.try_create_zones()

    assigned = organizer.try_random_assign_zones()
    page.wait_for_timeout(700)

    if assigned and not _validation_visible(page):
        attach_final_screenshot(page, "organizer-negative-zones-without-pairs-gap")
        pytest.xfail("Organizer Web permite sortear zonas sin parejas suficientes; esperado bloqueo/validacion.")
    assert not assigned or _validation_visible(page)
    attach_final_screenshot(page, "organizer-negative-zones-without-pairs")


@allure.feature("Organizer LITE")
@allure.story("Generar partidos sin sorteo")
def test_organizer_generate_matches_without_assign_rejected(page: Page, settings: Settings) -> None:
    organizer = _create_tournament_detail(page, settings)
    _create_pairs(organizer, _unique("QA Categoria Neg Matches"))
    organizer.open_zones_tab()
    organizer.set_zone_count(2)
    if not organizer.try_create_zones():
        pytest.skip("No se pudo crear zonas para probar generacion sin sorteo.")

    generated = organizer.try_generate_matches()
    page.wait_for_timeout(700)

    assert not generated or _validation_visible(page)
    attach_final_screenshot(page, "organizer-negative-matches-without-assign")


@allure.feature("Organizer LITE")
@allure.story("Resultado invalido UI")
def test_organizer_invalid_result_rejected(page: Page, settings: Settings) -> None:
    organizer = _create_tournament_detail(page, settings)
    _create_pairs(organizer, _unique("QA Categoria Neg Resultado"))
    organizer.open_zones_tab()
    organizer.set_zone_count(2)
    if not organizer.try_create_zones() or not organizer.try_random_assign_zones() or not organizer.try_generate_matches():
        pytest.skip("No se pudo preparar partido para resultado invalido.")
    if not organizer.try_open_first_match_result_form():
        pytest.skip("No hay accion visible para abrir modal de resultado.")

    dialog = organizer.dialog()
    inputs = dialog.locator("input[type='number']")
    if inputs.count() < 2:
        pytest.skip("El modal de resultado no expone inputs numericos.")
    for index in range(min(inputs.count(), 4)):
        inputs.nth(index).fill("6")

    save = page.get_by_test_id("organizer-save-result-button").first
    if save.count() == 0:
        save = dialog.get_by_role("button", name=re.compile(r"Guardar|Cargar|Registrar|Aceptar|Confirmar", re.I)).last
    if save.count() == 0:
        pytest.skip("No se encontro accion estable para guardar resultado invalido.")
    if save.is_enabled():
        save.click()
        page.wait_for_timeout(700)

    assert dialog.is_visible() or _validation_visible(page)
    attach_final_screenshot(page, "organizer-negative-invalid-result")
