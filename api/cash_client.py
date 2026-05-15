from api.base_client import BaseClient


class CashClient(BaseClient):
    def bookings_summary(self):
        return self.get("/api/admin/cash/summary/bookings")
