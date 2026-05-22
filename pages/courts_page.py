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

        card = court.first.locator("xpath=ancestor::article[1]")
        card.get_by_role("button", name="Eliminar").click()
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
