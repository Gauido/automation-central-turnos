import allure
import pytest

from api.bookings_client import BookingsClient


pytestmark = [pytest.mark.api, pytest.mark.booking, pytest.mark.smoke]


@allure.feature("API Reservas")
@allure.story("Crear reserva con tenant activo")
def test_api_create_booking_active_tenant(
    bookings_client: BookingsClient,
    api_booking: dict,
    api_tenants: dict,
) -> None:
    tenant_id = api_tenants["tenants"]["active"]["tenant_id"]
    if not tenant_id:
        pytest.skip("Missing tenants.active.tenant_id in tests/api/data/api_tenants.json")

    bookings_client.set_tenant(tenant_id)
    response = bookings_client.create_booking(api_booking["booking_payload"])
    body = response.json()

    assert response.status_code in (200, 201)
    assert body["success"] is True
    assert body.get("data")

    booking_id = body["data"].get("id")
    assert booking_id
    bookings_client.cancel_booking(booking_id)


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
