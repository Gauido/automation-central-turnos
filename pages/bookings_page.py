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

    def _new_booking_button(self):
        button = self.page.get_by_test_id("bookings-header-btn-new").first
        if button.count() > 0:
            return button
        return self.page.get_by_role("button", name="Nueva Reserva")

    def _next_day_button(self):
        button = self.page.get_by_test_id("bookings-new-btn-next-day").first
        if button.count() > 0:
            return button
        return self.page.get_by_role("button").filter(has_text=re.compile(r"›|>")).last

    def open_first_booking_details(self) -> None:
        action = self.page.locator("[data-testid^='bookings-row-action-detail-']").first
        if action.count() == 0:
            action = self.page.get_by_role("button", name="Acciones").first
        action.click()
        expect(self.page.get_by_text("Gestionar Reserva", exact=True)).to_be_visible()

    def has_visible_bookings(self) -> bool:
        empty = self.page.locator(".bk-empty").filter(has_text=re.compile(r"No se encontraron reservas|No hay reservas", re.I))
        if empty.count() > 0 and empty.first.is_visible():
            return False
        if self.page.locator("[data-testid^='bookings-row-']").count() > 0:
            return True
        return self.page.locator('[role="row"]').count() > 1

    def expect_booking_details(self) -> None:
        expect(self.page.get_by_role("heading", name=re.compile(r"Gestionar Reserva"))).to_be_visible()
        expect(self.page.get_by_text("Turno", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Detalle de pago", exact=True)).to_be_visible()
        expect(self.page.get_by_role("button", name="Cancelar reserva")).to_be_visible()

    def create_simple_booking(self, customer_search: str, customer_name: str, court_name: str | None = None) -> None:
        self.create_booking(customer_search, customer_name, court_name)

    def create_booking(self, customer_search: str, customer_name: str, court_name: str | None = None) -> dict[str, str]:
        booking_slot = self.start_booking_for_first_available_slot(customer_search, customer_name, court_name)
        self.submit_booking()
        expect(self.page.locator("app-new-booking-modal .modal-overlay")).not_to_be_visible(timeout=30000)
        expect(self.page.get_by_text(customer_name, exact=False).first).to_be_visible()
        return booking_slot

    def start_booking_for_first_available_slot(
        self,
        customer_search: str,
        customer_name: str,
        court_name: str | None = None,
    ) -> dict[str, str]:
        self._new_booking_button().click()
        self._next_day_button().click()
        slot = self._available_slot(court_name)
        expect(slot).to_be_visible()
        slot.click()
        booking_slot = self.selected_slot()

        search = self.page.get_by_test_id("bookings-new-customer-search").first
        if search.count() == 0:
            search = self.page.get_by_placeholder("Buscar por nombre o telefono...")
        search.fill(customer_search)
        customer = self.page.locator(".autocomplete-dropdown .autocomplete-item").filter(has_text=customer_name).first
        expect(customer).to_be_visible()
        customer.click()
        return booking_slot

    def _available_slot(self, court_name: str | None = None):
        if court_name:
            row = self.page.locator("[data-testid^='bookings-new-court-row-']").filter(has_text=court_name).first
            if row.count() == 0:
                row = self.page.locator("tr").filter(has_text=court_name).first
            expect(row).to_be_visible()
            slot = row.locator("[data-testid^='bookings-new-slot-']").first
            if slot.count() > 0:
                return slot
            return row.locator("td.slot-grid__cell--available").first
        slot = self.page.locator("[data-testid^='bookings-new-slot-']").first
        if slot.count() > 0:
            return slot
        return self.page.locator("td.slot-grid__cell--available").first

    def submit_booking(self) -> None:
        submit = self.page.get_by_test_id("bookings-new-btn-save").first
        if submit.count() == 0:
            submit = self.page.get_by_role("button", name="Crear Reserva")
        submit.click()

    def expect_booking_create_blocked(self) -> None:
        rejection = self.page.locator(".toast, .alert, [role='alert'], .form__api-error").filter(
            has_text=re.compile(r"(ocup|reserv|slot|horario|dispon|maximo|error|bloque)", re.IGNORECASE)
        )
        expect(rejection.first).to_be_visible(timeout=30000)

    def expect_booking_visible(self, customer_name: str) -> None:
        expect(self.page.get_by_text(customer_name, exact=False).first).to_be_visible()

    def selected_slot(self) -> dict[str, str]:
        badge = self.page.locator(".slot-selection__badge")
        expect(badge).to_be_visible()
        text = badge.inner_text().strip()
        separator = "·" if "·" in text else "Â·"
        court, times = [part.strip() for part in text.split(separator, maxsplit=1)]
        start_time, end_time = [part.strip() for part in times.split("-", maxsplit=1)]
        return {
            "court": court,
            "start_time": start_time,
            "end_time": end_time,
            "display_time": f"{start_time[:5]} – {end_time[:5]}",
            "grid_time": f"{start_time} → {end_time}",
        }

    def expect_slot_occupied(self, booking_slot: dict[str, str]) -> None:
        self._new_booking_button().click()
        self._next_day_button().click()
        row = self.page.locator("[data-testid^='bookings-new-court-row-']").filter(has_text=booking_slot["court"]).first
        if row.count() == 0:
            row = self.page.locator("tr").filter(has_text=booking_slot["court"]).first
        expect(row.get_by_text(booking_slot["display_time"], exact=True)).to_be_visible()
        expect(row.get_by_text("Reservado", exact=True)).to_be_visible()

    def open_booking_details_by_slot(self, booking_slot: dict[str, str], customer_name: str) -> None:
        row = (
            self.page.locator("[data-testid^='bookings-row-'], [role='row']")
            .filter(has_text=booking_slot["court"])
            .filter(has_text=booking_slot["grid_time"])
            .filter(has_text=customer_name)
            .first
        )
        expect(row).to_be_visible()
        action = row.locator("[data-testid^='bookings-row-action-detail-']").first
        if action.count() == 0:
            action = row.get_by_role("button", name="Acciones")
        action.click()
        self.expect_booking_details()

    def attempt_no_show(self) -> None:
        self.page.get_by_role("button", name="No se presentó").click()

    def expect_no_show_future_blocked(self) -> None:
        rejection = self.page.locator(".toast, .alert, [role='alert']").filter(
            has_text=re.compile(r"(futur|fecha|todav|no se puede|rechaz|error)", re.IGNORECASE)
        )
        expect(rejection.first).to_be_visible()

    def cancel_open_booking(self) -> None:
        self.page.get_by_role("button", name="Cancelar reserva").click()
        confirm = self.page.get_by_role("button", name="Cancelar reserva").last
        if confirm.count() > 0:
            confirm.click()
        expect(self.page.get_by_role("heading", name=re.compile(r"Gestionar Reserva"))).not_to_be_visible()

    def close_new_booking_modal(self) -> None:
        cancel = self.page.locator("app-new-booking-modal").get_by_role("button", name="Cancelar")
        if cancel.count() > 0:
            cancel.click()
