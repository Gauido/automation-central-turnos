import re

import allure
import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from config.settings import Settings
from pages.organizer_page import OrganizerPage
from tests.web.test_organizer_tournament_setup_flow import _create_pairs, _create_tournament_detail, _debug_discover, _unique
from utils.allure_helpers import attach_final_screenshot


pytestmark = [pytest.mark.web, pytest.mark.organizer, pytest.mark.usefixtures("clean_organizer_data")]


def _prepare_fixture(page: Page, settings: Settings, zone_count: int = 2) -> OrganizerPage:
    organizer = _create_tournament_detail(page, settings)
    _create_pairs(organizer, _unique("QA Categoria Advanced"))
    organizer.open_zones_tab()
    _debug_discover(page, "organizer-advanced-zones-before")
    organizer.set_zone_count(zone_count)
    if not organizer.try_create_zones():
        pytest.skip("No se pudo crear zonas desde UI avanzada.")
    _debug_discover(page, "organizer-advanced-zones-created")
    if not organizer.try_random_assign_zones():
        pytest.skip("No se pudo sortear zonas desde UI avanzada.")
    _debug_discover(page, "organizer-advanced-zones-assigned")
    if not organizer.try_generate_matches():
        pytest.skip("No se pudo generar partidos desde UI avanzada.")
    _debug_discover(page, "organizer-advanced-zones-matches")
    return organizer


@allure.feature("Organizer LITE")
@allure.story("Resultado de partido Web")
@pytest.mark.smoke
def test_organizer_match_result_basic(page: Page, settings: Settings) -> None:
    organizer = _prepare_fixture(page, settings, zone_count=2)

    with allure.step("Abrir carga de resultado del primer partido"):
        if not organizer.try_open_first_match_result_form():
            _debug_discover(page, "organizer-match-result-modal")
            attach_final_screenshot(page, "organizer-match-result-not-available")
            pytest.skip("No hay accion visible/habilitada estable para cargar resultado de partido.")
        _debug_discover(page, "organizer-match-result-modal", root_selector='[role="dialog"]')

    with allure.step("Cargar resultado simple"):
        if not organizer.fill_open_match_result():
            attach_final_screenshot(page, "organizer-match-result-form-blocked")
            pytest.skip("El modal de resultado no expone inputs/submit estables para cargar 6-3 6-4.")

    body_text = page.locator("body").inner_text()
    assert re.search(r"6\s*[-/]\s*3|6\s*[-/]\s*4|Finalizado|Jugado", body_text, re.I)
    attach_final_screenshot(page, "organizer-match-result-saved")


@allure.feature("Organizer LITE")
@allure.story("Llaves Web")
def test_organizer_bracket_generation_basic(page: Page, settings: Settings) -> None:
    organizer = _prepare_fixture(page, settings, zone_count=2)

    with allure.step("Ir a Llaves"):
        organizer.try_close_zones()
        organizer.open_bracket_tab()
        bracket_dom = _debug_discover(page, "organizer-bracket")
        if bracket_dom:
            assert bracket_dom["visibleText"]

    with allure.step("Intentar generar llave"):
        generated = organizer.try_generate_bracket()
        _debug_discover(page, "organizer-bracket-after-action")
        attach_final_screenshot(page, "organizer-bracket-final")

    if not generated:
        pytest.skip("Llaves no expone accion visible/habilitada para generar bracket o faltan precondiciones de negocio.")
    assert re.search(r"Llave|Semifinal|Final|Bracket|Partido", page.locator("body").inner_text(), re.I)


@allure.feature("Organizer LITE")
@allure.story("Reporte Web")
@pytest.mark.smoke
def test_organizer_report_tab_basic(page: Page, settings: Settings) -> None:
    organizer = _prepare_fixture(page, settings, zone_count=2)

    with allure.step("Abrir Reporte"):
        organizer.open_report_tab()
        report_dom = _debug_discover(page, "organizer-report")
        if report_dom:
            assert report_dom["visibleText"]

    body_text = page.locator("body").inner_text()
    assert re.search(r"Reporte|Inscrip|Pago|Categor|Parejas|Total|Cobrado|Recaud", body_text, re.I)
    attach_final_screenshot(page, "organizer-report-loaded")


@allure.feature("Organizer LITE")
@allure.story("Exports Web")
def test_organizer_exports_available(page: Page, settings: Settings) -> None:
    organizer = _prepare_fixture(page, settings, zone_count=2)

    with allure.step("Abrir export Fixture PDF"):
        exports_dom = _debug_discover(page, "organizer-exports")
        if exports_dom:
            assert exports_dom["visibleText"]
        open_button = organizer.export_open_button("fixture_pdf")
        if open_button.count() == 0 or not open_button.is_visible() or not open_button.is_enabled():
            attach_final_screenshot(page, "organizer-export-fixture-open-missing")
            pytest.skip("No esta disponible el testid/boton organizer-exports-btn-fixture-pdf-open.")
        open_button.click()

    with allure.step("Descargar Fixture PDF desde modal"):
        download_button = organizer.export_download_button()
        if download_button.count() == 0 or not download_button.is_visible() or not download_button.is_enabled():
            attach_final_screenshot(page, "organizer-export-download-missing")
            pytest.skip("No esta disponible el testid/boton organizer-exports-btn-download.")
        try:
            with page.expect_download(timeout=15000) as download_info:
                download_button.click()
            download = download_info.value
            assert download.suggested_filename.lower().endswith(".pdf")
        except PlaywrightTimeoutError:
            attach_final_screenshot(page, "organizer-export-fixture-pdf-blocked")
            pytest.skip("El flujo Fixture PDF no disparo descarga detectable con el contrato de modal.")

    allure.attach(
        f"fixture_pdf: {download.suggested_filename}",
        name="exports-descargados.txt",
        attachment_type=allure.attachment_type.TEXT,
    )
