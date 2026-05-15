import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class BookingsPage(BasePage):
    path = "/bookings"

    def open(self) -> None:
        if self.page.get_by_role("button", name="Gestionar").count() > 0:
            self.page.get_by_role("button", name="Gestionar").first.click()
        self.goto(self.path)
        expect(self.page.get_by_role("heading", name="Reservas", exact=True)).to_be_visible()

    def open_first_booking_details(self) -> None:
        self.page.get_by_role("button", name="Acciones").first.click()
        expect(self.page.get_by_text("Gestionar Reserva", exact=True)).to_be_visible()

    def expect_booking_details(self) -> None:
        expect(self.page.get_by_text("Cancha:", exact=False)).to_be_visible()
        expect(self.page.get_by_text("Fecha:", exact=False)).to_be_visible()
        expect(self.page.get_by_text("Horario:", exact=False)).to_be_visible()

    def create_simple_booking(self, customer_search: str, customer_name: str) -> None:
        self.page.get_by_role("button", name="Nueva Reserva").click()
        self.page.get_by_role("button", name="›").last.click()
        slot = self.page.locator("td.slot-grid__cell--available").first
        expect(slot).to_be_visible()
        slot.click()

        self.page.get_by_placeholder("Buscar por nombre o telefono...").fill(customer_search)
        customer = self.page.get_by_text(customer_name, exact=True).last
        expect(customer).to_be_visible()
        customer.click()

        self.page.get_by_role("button", name="Crear Reserva").click()
        expect(self.page.get_by_text(customer_name, exact=False).first).to_be_visible()

    def expect_booking_visible(self, customer_name: str) -> None:
        expect(self.page.get_by_text(customer_name, exact=False).first).to_be_visible()
