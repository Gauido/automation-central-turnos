from dataclasses import dataclass

from config.settings import Settings


@dataclass(frozen=True)
class Credentials:
    email: str
    password: str


def admin_credentials(settings: Settings) -> Credentials:
    if not settings.admin_email or not settings.admin_password:
        raise ValueError("CT_ADMIN_EMAIL and CT_ADMIN_PASSWORD are required")
    return Credentials(email=settings.admin_email, password=settings.admin_password)

