from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import allure


SENSITIVE_KEYS = {
    "authorization",
    "x-qa-token",
    "cookie",
    "password",
    "access_token",
    "refresh_token",
    "token",
}


def sanitize_context(value: Any) -> Any:
    if isinstance(value, Mapping):
        sanitized = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = sanitize_context(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_context(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_context(item) for item in value]
    return value


def attach_test_context(**context: Any) -> None:
    payload = sanitize_context(context)
    with allure.step("Datos del test"):
        allure.attach(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False),
            name="datos-del-test.json",
            attachment_type=allure.attachment_type.JSON,
        )
