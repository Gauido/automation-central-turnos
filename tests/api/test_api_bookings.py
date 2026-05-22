import allure
import httpx
import pytest

from api.bookings_client import BookingsClient
from api.qa_client import QaClient


pytestmark = [pytest.mark.api, pytest.mark.booking, pytest.mark.smoke]


@allure.feature("API Reservas")
@allure.story("Crear reserva con tenant activo")
def test_api_create_booking_active_tenant(
    bookings_client: BookingsClient,
    qa_client: QaClient,
    api_booking: dict,
    api_tenants: dict,
) -> None:
    tenant_id = api_tenants["tenants"]["active"]["tenant_id"]
    if not tenant_id:
        pytest.skip("Missing tenants.active.tenant_id in tests/api/data/api_tenants.json")
    if api_booking.get("qa_controlled") is not True:
        pytest.skip("API booking data not QA-controlled yet")

    qa_client.reset_customer_silent(api_booking["customer_clean_id"])
    bookings_client.set_tenant(tenant_id)
    try:
        try:
            response = bookings_client.create_booking(api_booking["booking_payload"])
        except httpx.RequestError as exc:
            pytest.skip(f"API booking endpoint unavailable: {exc.__class__.__name__}")
        try:
            body = response.json()
        except ValueError:
            pytest.skip("API booking endpoint returned non-JSON response")

        assert response.status_code in (200, 201)
        assert body["success"] is True
        assert body.get("data")

        booking_id = body["data"].get("id")
        assert booking_id
        bookings_client.cancel_booking(booking_id)
    finally:
        qa_client.reset_customer_silent(api_booking["customer_clean_id"])


@allure.feature("API Reservas")
@allure.story("Tenant vencido bloquea reserva")
def test_api_create_booking_expired_tenant_blocked(
    bookings_client: BookingsClient,
    api_booking: dict,
    api_tenants: dict,
) -> None:
    tenant_id = api_tenants["tenants"]["expired"]["tenant_id"]
    if not tenant_id:
        pytest.skip("Missing tenants.expired.tenant_id in tests/api/data/api_tenants.json")

    bookings_client.set_tenant(tenant_id)
    response = bookings_client.create_booking(api_booking["booking_payload"])
    body = response.json()

    assert response.status_code in (400, 402)
    assert body["success"] is False
    assert "suscripción" in body["message"].lower()
