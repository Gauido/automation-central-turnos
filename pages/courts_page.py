import re

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from pages.base_page import BasePage


class CourtsPage(BasePage):
    path = "/courts"

    def open(self) -> None:
        if self.page.get_by_role("button", name="Gestionar").count() > 0:
            self.page.get_by_role("button", name="Gestionar").first.click()
        self.goto(self.path)
        expect(self.page.get_by_text("Gestion de Canchas", exact=True)).to_be_visible()

    def create_court(self, name: str, number: int) -> None:
        create = self.page.get_by_test_id("courts-header-btn-create").first
        if create.count() == 0:
            create = self.page.get_by_role("button", name="Agregar Cancha")
        create.click()

        number_input = self.page.get_by_test_id("courts-create-input-number").first
        if number_input.count() == 0:
            number_input = self.page.locator("input[name='number']").first
        number_input.fill(str(number))

        name_input = self.page.get_by_test_id("courts-create-input-name").first
        if name_input.count() == 0:
            name_input = self.page.locator("input[name='name']").first
        name_input.fill(name)

        save = self.page.get_by_test_id("courts-create-btn-save").first
        if save.count() == 0:
            save = self.page.get_by_role("button", name="Crear")
        save.click()
        self.wait_for_court_created(name)

    def wait_for_court_created(self, name: str) -> None:
        toast = self.page.locator(".toast, [role='alert']").filter(has_text=re.compile(r"cancha creada|creada", re.I))
        try:
            expect(toast.first).to_be_visible(timeout=10000)
        except PlaywrightTimeoutError:
            pass

        try:
            self.expect_court_visible(name)
        except AssertionError:
            self.page.reload(wait_until="networkidle")
            expect(self.page.get_by_text("Gestion de Canchas", exact=True)).to_be_visible()
            self.expect_court_visible(name)

    def expect_court_visible(self, name: str) -> None:
        expect(self.find_court_by_name(name)).to_be_visible()

    def expect_court_not_visible(self, name: str) -> None:
        expect(self.page.get_by_text(name, exact=True)).not_to_be_visible()

    def delete_court_by_name(self, name: str) -> None:
        if not name.startswith("QA_AUTO_CANCHA"):
            raise ValueError("Refusing to delete non-QA court")

        court = self.find_court_by_name(name, fail_if_missing=False)
        if court.count() == 0:
            return

        card = self.page.locator("[data-testid^='courts-card-']").filter(has_text=name).first
        if card.count() > 0:
            delete = card.locator("[data-testid^='courts-card-btn-delete-']").first
        else:
            card = court.first.locator("xpath=ancestor::article[1]")
            delete = card.get_by_role("button", name="Eliminar")
        delete.click()
        self.page.get_by_role("button", name="Eliminar").last.click()
        expect(self.page.get_by_text(name, exact=True)).not_to_be_visible()

    def find_court_by_name(self, name: str, fail_if_missing: bool = True):
        for _ in range(5):
            court = self.page.get_by_text(name, exact=True)
            if court.count() > 0 and court.first.is_visible():
                return court.first

            next_button = self.page.locator("app-paginator .paginator__btn").last
            if next_button.count() == 0 or next_button.is_disabled():
                break

            next_button.click()
            expect(self.page.locator(".ct-card").first).to_be_visible()

        if fail_if_missing:
            raise AssertionError(f"Court not visible in paginated list: {name}")
        return self.page.get_by_text(name, exact=True)
