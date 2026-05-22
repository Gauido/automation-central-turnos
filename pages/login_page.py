import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def open(self) -> None:
        self.goto(self.path)

    def login(self, email: str, password: str) -> None:
        self.page.get_by_placeholder("Email").fill(email)
        self.page.get_by_placeholder("Contraseña").fill(password)
        self.page.get_by_role("button", name="Iniciar Sesion").click()

    def expect_logged_in(self) -> None:
        expect(self.page).not_to_have_url(re.compile(r".*/login(?:[/?#].*)?$"))

    def expect_invalid_login(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/login(?:[/?#].*)?$"))
        expect(
            self.page.locator(".toast, .alert, [role='alert'], .form__api-error").filter(
                has_text=re.compile(r"(credencial|invalid|incorrect|error|no autorizado)", re.IGNORECASE)
            ).first
        ).to_be_visible()
