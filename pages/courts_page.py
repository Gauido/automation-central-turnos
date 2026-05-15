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
        self.page.get_by_role("button", name="Agregar Cancha").click()
        self.page.locator("input[name='number']").fill(str(number))
        self.page.locator("input[name='name']").fill(name)
        self.page.get_by_role("button", name="Crear").click()
        expect(self.page.get_by_text(name, exact=True)).to_be_visible()

    def expect_court_visible(self, name: str) -> None:
        expect(self.page.get_by_text(name, exact=True)).to_be_visible()

    def expect_court_not_visible(self, name: str) -> None:
        expect(self.page.get_by_text(name, exact=True)).not_to_be_visible()

    def delete_court_by_name(self, name: str) -> None:
        if not name.startswith("QA_AUTO_CANCHA"):
            raise ValueError("Refusing to delete non-QA court")

        court = self.page.get_by_text(name, exact=True)
        if court.count() == 0:
            return

        card = court.first.locator("xpath=ancestor::article[1]")
        card.get_by_role("button", name="Eliminar").click()
        self.page.get_by_role("button", name="Eliminar").last.click()
        expect(self.page.get_by_text(name, exact=True)).not_to_be_visible()
