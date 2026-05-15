from api.base_client import BaseClient


class BookingsClient(BaseClient):
    def create_booking(self, payload: dict):
        return self.post("/api/bookings", json=payload)

    def cancel_booking(self, booking_id: int | str):
        return self.post(f"/api/bookings/{booking_id}/cancel")

    def cash_payment(self, booking_id: int | str, payload: dict):
        return self.post(f"/api/bookings/{booking_id}/cash-payment", json=payload)

    def mark_no_show(self, booking_id: int | str):
        return self.post(f"/api/bookings/{booking_id}/mark-no-show")
