import re
from datetime import datetime
from pathlib import Path

import allure
from playwright.sync_api import expect

from pages.base_page import BasePage
from utils.report_config import is_debug_report


class OrganizerPage(BasePage):
    path = "/organizer"
    title_pattern = re.compile(r"Organizer|Organizador|Torneos", re.I)
    detail_tabs = (
        ("categories", re.compile(r"Categor(?:i|\u00ed)as", re.I)),
        ("pairs", re.compile(r"Parejas", re.I)),
        ("zones", re.compile(r"Zonas", re.I)),
        ("bracket", re.compile(r"Llaves", re.I)),
        ("report", re.compile(r"Reporte", re.I)),
        ("today", re.compile(r"Hoy", re.I)),
    )

    def open(self) -> None:
        self.goto(self.path)

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/organizer(?:[/?#].*)?$"))
        expect(self.main_title()).to_be_visible(timeout=15000)

    def main_title(self):
        heading = self.page.get_by_role("heading", name=self.title_pattern).first
        if heading.count() > 0:
            return heading
        return self.page.get_by_text(self.title_pattern).first

    def create_tournament_button(self):
        test_id = self.page.get_by_test_id("organizer-create-tournament-button").first
        if test_id.count() > 0:
            return test_id
        new_tournament = self.page.get_by_role("button", name=re.compile(r"^\s*(\+\s*)?Nuevo torneo\s*$", re.I)).first
        if new_tournament.count() > 0:
            return new_tournament
        return self.page.get_by_role("button", name=re.compile(r"Nuevo torneo|Crear torneo", re.I)).first

    def open_create_tournament(self) -> None:
        button = self.create_tournament_button()
        expect(button).to_be_visible(timeout=10000)
        button.click()
        self.page.wait_for_timeout(1000)
        if is_debug_report():
            self.capture_create_tournament_diagnostics()

    def capture_create_tournament_diagnostics(self) -> dict:
        Path("screenshots").mkdir(parents=True, exist_ok=True)
        screenshot = self.page.screenshot(path="screenshots/organizer-create-form.png", full_page=True)
        allure.attach(
            screenshot,
            name="organizer-create-form.png",
            attachment_type=allure.attachment_type.PNG,
        )

        diagnostics = self.page.evaluate(
            """() => {
                const selectors = [
                    'input',
                    'textarea',
                    '[formcontrolname]',
                    '[ng-reflect-name]',
                    '[aria-label]',
                    'mat-dialog-container input',
                    '.modal input',
                    'input[type="text"]'
                ];
                const selectorCounts = Object.fromEntries(
                    selectors.map((selector) => [selector, document.querySelectorAll(selector).length])
                );
                const fields = Array.from(document.querySelectorAll('input, textarea, [formcontrolname], [ng-reflect-name], [aria-label]'))
                    .map((el) => ({
                        tag: el.tagName.toLowerCase(),
                        type: el.getAttribute('type'),
                        id: el.id || null,
                        name: el.getAttribute('name'),
                        placeholder: el.getAttribute('placeholder'),
                        ariaLabel: el.getAttribute('aria-label'),
                        formControlName: el.getAttribute('formcontrolname'),
                        ngReflectName: el.getAttribute('ng-reflect-name'),
                        text: (el.innerText || el.value || '').trim().slice(0, 120),
                        visible: !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length),
                    }));
                const dialog = document.querySelector('mat-dialog-container, [role="dialog"], .modal, form');
                const html = (dialog || document.body).outerHTML.slice(0, 6000);
                return { selectorCounts, fields, html };
            }"""
        )
        allure.attach(
            diagnostics["html"],
            name="organizer-create-form.html",
            attachment_type=allure.attachment_type.HTML,
        )
        allure.attach(
            str(diagnostics),
            name="organizer-create-form-diagnostics.txt",
            attachment_type=allure.attachment_type.TEXT,
        )
        return diagnostics

    def tournament_name_input(self):
        test_id = self.page.get_by_test_id("organizer-tournament-name-input").first
        if test_id.count() > 0:
            return test_id
        label = self.page.get_by_label(re.compile(r"Nombre", re.I)).first
        if label.count() > 0:
            return label
        placeholder = self.page.get_by_placeholder(re.compile(r"Nombre", re.I)).first
        if placeholder.count() > 0:
            return placeholder
        dialog_input = self.page.get_by_role("dialog").locator("input[placeholder='Ej: Apertura 2026']").first
        if dialog_input.count() > 0:
            return dialog_input
        return self.page.locator(".modal input[placeholder='Ej: Apertura 2026']").first

    def save_tournament_button(self):
        test_id = self.page.get_by_test_id("organizer-save-tournament-button").first
        if test_id.count() > 0:
            return test_id
        return self.page.get_by_role("button", name=re.compile(r"Crear|Guardar|Aceptar", re.I)).first

    def create_basic_tournament(self, name: str | None = None) -> str:
        tournament_name = name or f"QA UI Organizer {datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.open_create_tournament()
        name_input = self.tournament_name_input()
        expect(name_input).to_be_visible(timeout=10000)
        name_input.fill(tournament_name)
        save = self.save_tournament_button()
        expect(save).to_be_visible(timeout=10000)
        save.click()
        self.expect_tournament_visible_or_detail(tournament_name)
        return tournament_name

    def expect_tournament_visible_or_detail(self, name: str) -> None:
        visible_name = self.page.get_by_text(name, exact=False).first
        expect(visible_name).to_be_visible(timeout=15000)

    def open_tournament_detail(self, name: str) -> None:
        link = self.page.get_by_role("link", name=re.compile(re.escape(name), re.I)).first
        if link.count() > 0:
            link.click()
        else:
            self.page.get_by_text(name, exact=False).first.click()
        expect(self.page.get_by_text(name, exact=False).first).to_be_visible(timeout=15000)

    def detail_tab(self, slug: str, label_pattern: re.Pattern):
        test_id = self.page.get_by_test_id(f"organizer-tabs-{slug}").first
        if test_id.count() > 0:
            return test_id
        role_tab = self.page.get_by_role("tab", name=label_pattern).first
        if role_tab.count() > 0:
            return role_tab
        return self.page.get_by_text(label_pattern).first

    def expect_detail_tabs_visible(self) -> None:
        for slug, label_pattern in self.detail_tabs:
            expect(self.detail_tab(slug, label_pattern)).to_be_visible(timeout=10000)

    def open_tab(self, slug: str, label_pattern: re.Pattern) -> None:
        tab = self.detail_tab(slug, label_pattern)
        expect(tab).to_be_visible(timeout=10000)
        tab.click()
        self.page.wait_for_timeout(700)

    def open_categories_tab(self) -> None:
        self.open_tab("categories", re.compile(r"Categor(?:i|\u00ed)as", re.I))

    def open_pairs_tab(self) -> None:
        self.open_tab("pairs", re.compile(r"Parejas", re.I))

    def open_zones_tab(self) -> None:
        self.open_tab("zones", re.compile(r"Zonas", re.I))

    def open_bracket_tab(self) -> None:
        self.open_tab("bracket", re.compile(r"Llaves", re.I))

    def open_report_tab(self) -> None:
        self.open_tab("report", re.compile(r"Reporte", re.I))

    def dialog(self):
        return self.page.get_by_role("dialog").first

    def open_category_form(self) -> None:
        button = self.page.get_by_test_id("organizer-create-category-button").first
        if button.count() == 0:
            button = self.page.get_by_role("button", name=re.compile(r"Nueva categor|Crear primera categor", re.I)).first
        expect(button).to_be_visible(timeout=10000)
        button.click()
        expect(self.dialog()).to_be_visible(timeout=10000)

    def create_category_basic(self, name: str, price: int = 5000) -> None:
        self.open_category_form()
        self.fill_open_category_form(name, price)

    def fill_open_category_form(self, name: str, price: int = 5000) -> None:
        dialog = self.dialog()
        name_input = self.page.get_by_test_id("organizer-category-name-input").first
        if name_input.count() == 0:
            name_input = dialog.locator("input:not([type='number'])").first
        if name_input.count() > 0:
            expect(name_input).to_be_visible(timeout=10000)
            name_input.fill(name)

        number_inputs = dialog.locator("input[type='number']")
        if number_inputs.count() > 0:
            number_inputs.first.fill(str(price))
        if number_inputs.count() > 1:
            number_inputs.nth(1).fill("2")

        save = self.page.get_by_test_id("organizer-save-category-button").first
        if save.count() == 0:
            save = dialog.get_by_role("button", name=re.compile(r"Crear|Guardar|Aceptar", re.I)).last
        expect(save).to_be_visible(timeout=10000)
        save.click()
        expect(dialog).not_to_be_visible(timeout=10000)
        expected_name = name if name_input.count() > 0 else "Primera"
        expect(self.page.get_by_text(expected_name, exact=False).first).to_be_visible(timeout=15000)

    def open_pair_form(self) -> None:
        button = self.page.get_by_test_id("organizer-create-pair-button").first
        if button.count() == 0:
            button = self.page.get_by_role(
                "button",
                name=re.compile(r"Nueva pareja|Agregar pareja|Crear pareja|Inscribir pareja|Inscribir la primera", re.I),
            ).first
        expect(button).to_be_visible(timeout=10000)
        button.click()
        expect(self.dialog()).to_be_visible(timeout=10000)

    def create_pair_basic(self, player1: str, player2: str) -> None:
        self.open_pair_form()
        self.fill_open_pair_form(player1, player2)

    def fill_open_pair_form(self, player1: str, player2: str) -> None:
        dialog = self.dialog()
        inputs = dialog.locator("input")
        if inputs.count() < 2:
            raise AssertionError("El modal de pareja no expone al menos 2 inputs visibles.")
        inputs.nth(0).fill(player1)
        inputs.nth(1).fill(player2)
        save = self.page.get_by_test_id("organizer-save-pair-button").first
        if save.count() == 0:
            save = dialog.get_by_role("button", name=re.compile(r"Crear|Guardar|Aceptar|Inscribir", re.I)).last
        expect(save).to_be_visible(timeout=10000)
        save.click()
        expect(self.page.get_by_text(player1, exact=False).first).to_be_visible(timeout=15000)
        expect(self.page.get_by_text(player2, exact=False).first).to_be_visible(timeout=15000)

    def try_random_assign_zones(self) -> bool:
        button = self.page.get_by_role(
            "button",
            name=re.compile(r"Aleatorio|Sortear|Asignar|Random|Distribuir", re.I),
        ).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.confirm_open_dialog(re.compile(r"Aleatorio|Sortear|Asignar|Confirmar|Aceptar", re.I))
        self.page.wait_for_timeout(1200)
        return True

    def set_zone_count(self, count: int) -> bool:
        zone_count = self.page.get_by_label(re.compile(r"Cantidad de zonas", re.I)).first
        if zone_count.count() == 0:
            zone_count = self.page.locator("input[type='number']").first
        if zone_count.count() == 0 or not zone_count.is_visible() or not zone_count.is_enabled():
            return False
        zone_count.fill(str(count))
        self.page.wait_for_timeout(300)
        return True

    def try_create_zones(self) -> bool:
        button = self.page.get_by_role("button", name=re.compile(r"Crear zonas", re.I)).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.confirm_open_dialog(re.compile(r"Crear zonas|Confirmar|Aceptar", re.I))
        self.page.wait_for_timeout(1200)
        return True

    def try_generate_matches(self) -> bool:
        button = self.page.get_by_role("button", name=re.compile(r"^\s*Generar partidos\s*$", re.I)).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.confirm_open_dialog(re.compile(r"Generar partidos|Generar|Confirmar|Aceptar", re.I))
        self.page.wait_for_timeout(1200)
        return True

    def confirm_open_dialog(self, button_name: re.Pattern) -> bool:
        dialog = self.dialog()
        if dialog.count() == 0 or not dialog.is_visible():
            return False
        button = dialog.get_by_role("button", name=button_name).last
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        expect(dialog).not_to_be_visible(timeout=10000)
        return True

    def try_open_first_match_result_form(self) -> bool:
        button = self.page.get_by_test_id("organizer-match-result-button").first
        if button.count() == 0:
            button = self.page.get_by_role(
                "button",
                name=re.compile(r"Resultado|Cargar resultado|Editar resultado|Registrar resultado|Anotar", re.I),
            ).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.page.wait_for_timeout(700)
        return self.dialog().count() > 0 and self.dialog().is_visible()

    def fill_open_match_result(self) -> bool:
        dialog = self.dialog()
        if dialog.count() == 0 or not dialog.is_visible():
            return False
        inputs = dialog.locator("input[type='number']")
        if inputs.count() < 4:
            return False
        winner = dialog.get_by_role("button", name=re.compile(r"Pareja A", re.I)).first
        if winner.count() > 0 and winner.is_visible() and winner.is_enabled():
            winner.click()
        for index, value in enumerate(("6", "3", "6", "4")):
            inputs.nth(index).fill(value)
        save = self.page.get_by_test_id("organizer-save-result-button").first
        if save.count() == 0:
            save = dialog.get_by_role("button", name=re.compile(r"Guardar|Cargar|Registrar|Aceptar|Confirmar", re.I)).last
        if save.count() == 0 or not save.is_visible() or not save.is_enabled():
            return False
        save.click()
        expect(dialog).not_to_be_visible(timeout=10000)
        self.page.wait_for_timeout(1000)
        return True

    def try_close_zones(self) -> bool:
        button = self.page.get_by_role("button", name=re.compile(r"Cerrar zonas|Cerrar zona|Finalizar zonas", re.I)).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.confirm_open_dialog(re.compile(r"Cerrar|Confirmar|Aceptar", re.I))
        self.page.wait_for_timeout(1000)
        return True

    def try_generate_bracket(self) -> bool:
        button = self.page.get_by_role(
            "button",
            name=re.compile(r"Generar llave|Crear llave|Armar llave|Generar bracket|Build bracket", re.I),
        ).first
        if button.count() == 0 or not button.is_visible() or not button.is_enabled():
            return False
        button.click()
        self.confirm_open_dialog(re.compile(r"Generar|Crear|Confirmar|Aceptar", re.I))
        self.page.wait_for_timeout(1200)
        return True

    def export_buttons(self):
        return {
            "fixture_pdf": self.page.get_by_role("button", name=re.compile(r"Fixture PDF", re.I)).first,
            "standings_pdf": self.page.get_by_role("button", name=re.compile(r"Posiciones PDF|Standings PDF", re.I)).first,
            "matches_excel": self.page.get_by_role("button", name=re.compile(r"Partidos Excel|Matches Excel", re.I)).first,
            "closure_pdf": self.page.get_by_role("button", name=re.compile(r"Cierre PDF", re.I)).first,
            "podium_pdf": self.page.get_by_role("button", name=re.compile(r"Podio PDF", re.I)).first,
        }
