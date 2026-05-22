import pytest


def require_controlled_booking_customer(booking: dict) -> None:
    if booking.get("qa_controlled_customer") is True:
        return

    pytest.skip(
        "Falta customer QA controlado para reservas: cliente existente con menos de 3 reservas activas futuras."
    )


def require_web_booking_create_enabled(booking: dict) -> None:
    if booking.get("web_booking_create_enabled") is True:
        return

    pytest.skip("WEB booking create blocked: endpoint normal queda colgado/timeoutea.")


def require_user(user: dict, role: str) -> None:
    if user.get("email") and user.get("password"):
        return

    pytest.skip(f"Falta usuario {role} con email/password en JSON.")
