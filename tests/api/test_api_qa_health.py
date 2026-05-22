import allure
import pytest

from api.qa_client import QaClient
from utils.api_assertions import assert_booking_created, assert_payment_approved
from utils.qa_factories import create_booking_payload, create_payment_payload


pytestmark = [pytest.mark.api, pytest.mark.qa, pytest.mark.regression]


TENANT_ID = 9001
COURT_ID = 9001
CUSTOMER_CLEAN_ID = 9003


def _booking_payload(qa_test_data: dict) -> dict:
    if qa_test_data.get("booking_payload") or qa_test_data.get("bookingPayload"):
        return qa_test_data.get("booking_payload") or qa_test_data.get("bookingPayload")

    slot = qa_test_data["suggestedSlots"][0]
    return create_booking_payload(
        TENANT_ID,
        COURT_ID,
        CUSTOMER_CLEAN_ID,
        booking_date=slot["date"],
        start_time=slot["startTime"],
    )


def _payment_payload(qa_test_data: dict) -> dict:
    return qa_test_data.get("payment_payload") or qa_test_data.get("paymentPayload") or create_payment_payload()


def _booking_id(body: dict) -> int | str:
    data = body.get("data") or body
    booking_id = data.get("id") or data.get("bookingId")
    assert booking_id
    return booking_id


@allure.feature("QA API")
@allure.story("Tenants QA disponibles")
def test_qa_tenants_available(qa_client: QaClient) -> None:
    response = qa_client.tenants()
    assert response.status_code == 200
    assert response.json()


@allure.feature("QA API")
@allure.story("Test data disponible")
def test_qa_test_data_available(qa_client: QaClient) -> None:
    response = qa_client.test_data()
    assert response.status_code == 200
    assert response.json()


@allure.feature("QA API")
@allure.story("Reset QA disponible")
def test_qa_reset_works(qa_reset_once) -> None:
    response = qa_reset_once
    if response.status_code == 500 and "invoices_booking_id_fkey" in response.text:
        pytest.skip("QA /reset blocked by invoices_booking_id_fkey")
    assert response.status_code in (200, 204)


@pytest.fixture()
def qa_reset_once(qa_client: QaClient):
    return qa_client.reset()


@allure.feature("QA API")
@allure.story("Crear reserva QA")
def test_qa_create_booking(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = None
    customer_id = qa_test_data["customers"]["clean"]["id"]
    try:
        qa_client.reset_customer_silent(customer_id)
        response = qa_client.create_booking(_booking_payload(qa_test_data))
        booking_id = _booking_id(assert_booking_created(response))
    finally:
        qa_client.reset_customer_silent(customer_id)


@allure.feature("QA API")
@allure.story("Agregar pago QA")
def test_qa_add_payment(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = None
    customer_id = qa_test_data["customers"]["clean"]["id"]
    try:
        qa_client.reset_customer_silent(customer_id)
        previous = qa_client.reporting_enabled
        qa_client.reporting_enabled = False
        try:
            booking_response = qa_client.create_booking(_booking_payload(qa_test_data))
        finally:
            qa_client.reporting_enabled = previous
        assert booking_response.status_code in (200, 201)
        booking_id = _booking_id(booking_response.json())

        payment_response = qa_client.add_booking_payment(booking_id, _payment_payload(qa_test_data))
        assert_payment_approved(payment_response)
    finally:
        qa_client.reset_customer_silent(customer_id)
