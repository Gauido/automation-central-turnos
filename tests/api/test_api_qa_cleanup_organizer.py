from datetime import date, timedelta

import allure
import pytest

from api.auth_client import AuthClient
from api.organizer_client import OrganizerClient
from api.qa_client import QaClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.organizer, pytest.mark.qa]

TENANT_ID = "9001"


def _data(response):
    body = response.json()
    assert isinstance(body, dict)
    assert body.get("success", True) is not False
    return body.get("data") or body


def _id(value: dict, *keys: str):
    for key in (*keys, "id"):
        if isinstance(value, dict) and value.get(key):
            return value[key]
    return None


def _items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "rows", "data", "tournaments"):
            nested = value.get(key)
            if isinstance(nested, list):
                return nested
    return []


@pytest.fixture()
def organizer_client(settings: Settings, api_auth_client: AuthClient):
    if not settings.owner_email or not settings.owner_password:
        pytest.skip("Owner credentials no configuradas en entorno local.")

    login = api_auth_client.login_raw(settings.owner_email, settings.owner_password)
    if login.status_code != 200:
        pytest.skip(f"Owner login blocked. status={login.status_code}")

    body = login.json()
    token = (body.get("data") or {}).get("token") or body.get("accessToken") or body.get("token") or body.get("jwt")
    assert token

    client = OrganizerClient(
        str(settings.api_base_url),
        settings.api_timeout_seconds,
        verify=not settings.ignore_https_errors,
    )
    client.set_bearer_token(token)
    client.set_tenant(TENANT_ID)
    yield client
    client.close()


@allure.feature("QA Layer")
@allure.story("Cleanup Organizer")
def test_qa_cleanup_organizer_removes_tournaments(qa_client: QaClient, organizer_client: OrganizerClient) -> None:
    with allure.step("Limpiar Organizer antes del setup"):
        initial_cleanup = qa_client.cleanup_organizer()
        assert initial_cleanup["success"] is True

    today = date.today()
    with allure.step("Crear torneo Organizer por API"):
        created = _data(
            organizer_client.create_tournament(
                {
                    "name": f"QA Cleanup Organizer {today.isoformat()}",
                    "startDate": today.isoformat(),
                    "endDate": (today + timedelta(days=1)).isoformat(),
                    "status": "draft",
                }
            )
        )
        tournament_id = _id(created, "tournamentId")
        assert tournament_id

    with allure.step("Ejecutar cleanup Organizer"):
        cleanup = qa_client.cleanup_organizer()
        assert cleanup["success"] is True
        assert cleanup["tenantId"] == 9001
        assert cleanup["deletedCounts"]["tournaments"] >= 1

    with allure.step("Validar que el torneo no aparece en listado Organizer"):
        response = organizer_client.list_tournaments()
        assert response.status_code == 200
        tournaments = _items(_data(response))
        tournament_ids = {_id(item, "tournamentId") for item in tournaments}
        assert tournament_id not in tournament_ids
