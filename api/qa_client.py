from api.base_client import BaseClient


class QaClient(BaseClient):
    def __init__(self, base_url: str, token: str, timeout: float = 30.0, verify: bool = True) -> None:
        super().__init__(base_url, timeout, verify)
        self.client.headers["X-QA-Token"] = token

    def test_data(self):
        return self.get("/test-data")

    def tenants(self):
        return self.get("/tenants")

    def users(self):
        return self.get("/users")

    def reset(self):
        return self.post("/reset")

    def cleanup_bookings(self, payload: dict | None = None):
        return self.post("/cleanup/bookings", json=payload or {})

    def reset_customer(self, customer_id: int | str):
        return self.post(f"/reset-customer/{customer_id}")

    def reset_customer_silent(self, customer_id: int | str):
        return self.post_silent(f"/reset-customer/{customer_id}")

    def create_booking(self, payload: dict):
        return self.post("/bookings", json=payload)

    def create_booking_silent(self, payload: dict):
        return self.post_silent("/bookings", json=payload)

    def add_booking_payment(self, booking_id: int | str, payload: dict):
        return self.post(f"/bookings/{booking_id}/payment", json=payload)

    def set_booking_state(self, booking_id: int | str, payload: dict):
        return self.post(f"/bookings/{booking_id}/state", json=payload)

    def move_booking_to_past(self, booking_id: int | str):
        return self.post(f"/bookings/{booking_id}/move-to-past", json={})

    def move_booking_to_future(self, booking_id: int | str):
        return self.post(f"/bookings/{booking_id}/move-to-future", json={})

    def reset_cash_day(self, payload: dict | None = None):
        return self.post("/cash/reset-day", json=payload or {})

    def change_tenant_plan(self, tenant_id: int | str, payload: dict):
        return self.post(f"/tenant/{tenant_id}/change-plan", json=payload)

    def expire_tenant_plan(self, tenant_id: int | str):
        return self.post(f"/tenant/{tenant_id}/expire-plan")

    def restore_tenant_plan(self, tenant_id: int | str):
        return self.post(f"/tenant/{tenant_id}/restore-plan")

    def tenant_switch_data(self, payload: dict | None = None):
        return self.post("/tenant-switch-data", json=payload or {})
