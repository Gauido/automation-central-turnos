import re

import httpx


def _json(response: httpx.Response) -> dict:
    body = response.json()
    assert isinstance(body, dict)
    return body


def assert_booking_created(response: httpx.Response) -> dict:
    assert response.status_code in (200, 201)
    body = _json(response)
    assert body.get("success", True) is True
    data = body.get("data") or body
    assert data.get("id") or data.get("bookingId")
    return data


def assert_payment_approved(response: httpx.Response) -> dict:
    assert response.status_code in (200, 201)
    body = _json(response)
    assert body.get("success", True) is True
    text = str(body).lower()
    assert any(value in text for value in ("approved", "paid", "cash", "payment"))
    return body.get("data") or body


def assert_validation_error(response: httpx.Response, expected: str | None = None) -> dict:
    assert response.status_code in (400, 422)
    body = _json(response)
    if expected:
        assert re.search(expected, str(body), re.IGNORECASE)
    return body


def assert_business_rule(response: httpx.Response, expected: str | None = None) -> dict:
    assert response.status_code in (400, 402, 409, 422)
    body = _json(response)
    assert body.get("success", False) is False
    if expected:
        assert re.search(expected, str(body), re.IGNORECASE)
    return body
