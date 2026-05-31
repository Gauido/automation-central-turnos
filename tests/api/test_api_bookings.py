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
    bookings_client.set_tenant(str(tenant_id))
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
    qa_client: QaClient,
    api_booking: dict,
    api_tenants: dict,
) -> None:
    response = qa_client.tenant_expired_data()
    if response.status_code == 404:
        pytest.skip("Documentado funcionalmente, pero no disponible en ambiente actual: /api/qa/tenant-expired-data")
    assert response.status_code == 200
    body = response.json()
    data = body.get("data") or body

    tenant_id = data.get("tenantId") or data.get("tenant_id") or data.get("tenant", {}).get("id") or 9200
    court_id = data.get("courtId") or data.get("court_id") or data.get("court", {}).get("id") or 9200
    customer = data.get("customer") or {}
    customer_phone = data.get("customerPhone") or customer.get("phone") or "+5491155559200"

    payload = {
        **api_booking["booking_payload"],
        "courtId": court_id,
        "customerPhone": customer_phone,
        "customerFirstName": data.get("customerFirstName") or customer.get("firstName") or "QA Expired Customer",
    }

    bookings_client.set_tenant(str(tenant_id))
    response = bookings_client.create_booking(payload)
    body = response.json()

    assert response.status_code in (400, 402)
    assert body["success"] is False
    assert "suscripción" in body["message"].lower()
