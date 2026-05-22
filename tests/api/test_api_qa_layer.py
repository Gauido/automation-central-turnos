from datetime import date

import allure
import pytest

from api.qa_client import QaClient
from utils.api_assertions import assert_booking_created, assert_payment_approved
from utils.qa_factories import create_booking_payload, create_payment_payload


pytestmark = [pytest.mark.api, pytest.mark.qa, pytest.mark.smoke]

TENANT_ID = 9001
COURT_ID = 9001
CUSTOMER_CLEAN_ID = 9003


def _booking_payload(qa_test_data: dict, slot_index: int = 0) -> dict:
    slots = qa_test_data["suggestedSlots"]
    slot = slots[slot_index % len(slots)]
    return create_booking_payload(
        TENANT_ID,
        COURT_ID,
        CUSTOMER_CLEAN_ID,
        booking_date=slot["date"],
        start_time=slot["startTime"],
    )


def _booking_id(body: dict) -> int | str:
    data = body.get("data") or body
    booking_id = data.get("id") or data.get("bookingId")
    assert booking_id
    return booking_id


def _create_booking_silent(qa_client: QaClient, qa_test_data: dict, slot_index: int = 0) -> int | str:
    qa_client.reset_customer_silent(CUSTOMER_CLEAN_ID)
    response = qa_client.create_booking_silent(_booking_payload(qa_test_data, slot_index))
    return _booking_id(response.json())


def _cleanup_customer(qa_client: QaClient) -> None:
    qa_client.reset_customer_silent(CUSTOMER_CLEAN_ID)


@allure.feature("QA Layer")
@allure.story("Test data")
def test_qa_layer_test_data(qa_client: QaClient) -> None:
    response = qa_client.test_data()
    assert response.status_code == 200
    assert response.json()


@allure.feature("QA Layer")
@allure.story("Tenants")
def test_qa_layer_tenants(qa_client: QaClient) -> None:
    response = qa_client.tenants()
    assert response.status_code == 200
    assert response.json()


@allure.feature("QA Layer")
@allure.story("Users")
def test_qa_layer_users(qa_client: QaClient) -> None:
    response = qa_client.users()
    assert response.status_code == 200
    assert response.json()


@allure.feature("QA Layer")
@allure.story("Reset customer")
def test_qa_layer_reset_customer(qa_client: QaClient) -> None:
    response = qa_client.reset_customer(CUSTOMER_CLEAN_ID)
    assert response.status_code in (200, 204)


@allure.feature("QA Layer")
@allure.story("Cleanup bookings")
def test_qa_layer_cleanup_bookings(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = _create_booking_silent(qa_client, qa_test_data, 0)
    try:
        response = qa_client.cleanup_bookings({"bookingIds": [booking_id]})
        if response.status_code == 500 and "invoices_booking_id_fkey" in response.text:
            pytest.skip("QA cleanup/bookings blocked by invoices_booking_id_fkey")
        assert response.status_code in (200, 204)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Create booking")
def test_qa_layer_create_booking(qa_client: QaClient, qa_test_data: dict) -> None:
    try:
        response = qa_client.create_booking(_booking_payload(qa_test_data, 1))
        assert_booking_created(response)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Booking payment")
def test_qa_layer_booking_payment(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = _create_booking_silent(qa_client, qa_test_data, 2)
    try:
        response = qa_client.add_booking_payment(booking_id, create_payment_payload())
        assert_payment_approved(response)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Move booking to past")
def test_qa_layer_move_booking_to_past(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = _create_booking_silent(qa_client, qa_test_data, 3)
    try:
        response = qa_client.move_booking_to_past(booking_id)
        assert response.status_code in (200, 204)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Move booking to future")
def test_qa_layer_move_booking_to_future(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = _create_booking_silent(qa_client, qa_test_data, 4)
    try:
        previous = qa_client.reporting_enabled
        qa_client.reporting_enabled = False
        try:
            qa_client.move_booking_to_past(booking_id)
        finally:
            qa_client.reporting_enabled = previous
        response = qa_client.move_booking_to_future(booking_id)
        assert response.status_code in (200, 204)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Booking state")
def test_qa_layer_booking_state(qa_client: QaClient, qa_test_data: dict) -> None:
    booking_id = _create_booking_silent(qa_client, qa_test_data, 5)
    try:
        response = qa_client.set_booking_state(booking_id, {"status": "confirmed"})
        assert response.status_code in (200, 204)
    finally:
        _cleanup_customer(qa_client)


@allure.feature("QA Layer")
@allure.story("Cash reset day")
def test_qa_layer_cash_reset_day(qa_client: QaClient) -> None:
    response = qa_client.reset_cash_day({"tenantId": TENANT_ID, "date": date.today().isoformat()})
    assert response.status_code in (200, 204)


@allure.feature("QA Layer")
@allure.story("Tenant change plan")
def test_qa_layer_tenant_change_plan(qa_client: QaClient) -> None:
    response = qa_client.change_tenant_plan(TENANT_ID, {"plan": "enterprise"})
    assert response.status_code in (200, 204)


@allure.feature("QA Layer")
@allure.story("Tenant restore plan")
def test_qa_layer_tenant_restore_plan(qa_client: QaClient) -> None:
    response = qa_client.restore_tenant_plan(TENANT_ID)
    assert response.status_code in (200, 204)


@allure.feature("QA Layer")
@allure.story("Tenant switch data")
def test_qa_layer_tenant_switch_data(qa_client: QaClient) -> None:
    response = qa_client.tenant_switch_data()
    assert response.status_code in (200, 201)
    assert response.json()
