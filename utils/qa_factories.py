from datetime import date, timedelta
from itertools import count


_time_counter = count()


def future_date_generator(days_from_today: int = 30) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()


def booking_time_generator(start_hour: int = 8, slot_minutes: int = 90) -> str:
    slot = next(_time_counter) % 8
    minutes = (start_hour * 60) + (slot * slot_minutes)
    return f"{minutes // 60:02d}:{minutes % 60:02d}:00"


def create_customer_payload(
    first_name: str = "QA Customer",
    phone: str = "+5491001000001",
    email: str | None = None,
) -> dict:
    payload = {
        "firstName": first_name,
        "phone": phone,
    }
    if email:
        payload["email"] = email
    return payload


def create_booking_payload(
    tenant_id: int | str = 9001,
    court_id: int | str = 9001,
    customer_id: int | str = 9003,
    booking_date: str | None = None,
    start_time: str | None = None,
) -> dict:
    return {
        "tenantId": tenant_id,
        "courtId": court_id,
        "customerId": customer_id,
        "date": booking_date or future_date_generator(),
        "startTime": start_time or booking_time_generator(),
    }


def create_panel_booking_payload(
    court_id: int | str = 9001,
    customer_phone: str = "+5491155555503",
    customer_first_name: str = "QA Clean Customer",
    booking_date: str | None = None,
    start_time: str | None = None,
) -> dict:
    return {
        "courtId": court_id,
        "customerPhone": customer_phone,
        "customerFirstName": customer_first_name,
        "date": booking_date or future_date_generator(),
        "startTime": start_time or booking_time_generator(),
    }


def create_payment_payload(amount: int | float = 1000, method: str = "cash") -> dict:
    return {
        "amount": amount,
        "method": method,
    }
