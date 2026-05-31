import re

from playwright.sync_api import expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def open(self) -> None:
        self.goto(self.path)

    def login(self, email: str, password: str) -> None:
        email_input = self.page.get_by_placeholder(re.compile(r"Email|Correo", re.I)).first
        if email_input.count() == 0:
            email_input = self.page.get_by_label(re.compile(r"Email|Correo", re.I)).first

        password_input = self.page.get_by_placeholder(re.compile(r"Contrase", re.I)).first
        if password_input.count() == 0:
            password_input = self.page.get_by_label(re.compile(r"Contrase", re.I)).first

        email_input.fill(email)
        password_input.fill(password)

        submit = self.page.get_by_role("button", name=re.compile(r"Iniciar|Ingresar|Login|Sesion|Sesi", re.I)).first
        if submit.count() == 0:
            submit = self.page.locator("button[type='submit']").first
        submit.click()

    def expect_logged_in(self) -> None:
        expect(self.page).not_to_have_url(re.compile(r".*/login(?:[/?#].*)?$"))

    def expect_invalid_login(self) -> None:
        expect(self.page).to_have_url(re.compile(r".*/login(?:[/?#].*)?$"))
        expect(
            self.page.locator(".toast, .alert, [role='alert'], .form__api-error").filter(
                has_text=re.compile(r"(credencial|invalid|incorrect|error|no autorizado)", re.IGNORECASE)
            ).first
        ).to_be_visible()
