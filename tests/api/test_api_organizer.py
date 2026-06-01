from datetime import date, timedelta

import allure
import pytest

from api.auth_client import AuthClient
from api.organizer_client import OrganizerClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.organizer, pytest.mark.usefixtures("clean_organizer_data")]

TENANT_ID = "9001"


def _body(response):
    body = response.json()
    assert isinstance(body, dict)
    return body


def _data(response):
    body = _body(response)
    assert body.get("success", True) is not False
    return body.get("data") or body


def _id(value: dict, *keys: str):
    if isinstance(value, dict) and isinstance(value.get("zone"), dict):
        value = value["zone"]
    for key in (*keys, "id"):
        if isinstance(value, dict) and value.get(key):
            return value[key]
    return None


def _items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "rows", "data", "matches", "pairs", "zones"):
            nested = value.get(key)
            if isinstance(nested, list):
                return nested
    return []


def _assert_success(response, expected=(200, 201)):
    assert response.status_code in expected
    return _data(response)


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


@pytest.fixture()
def organizer_tournament(organizer_client: OrganizerClient):
    tournament_id = None
    today = date.today()
    try:
        with allure.step("Crear torneo Organizer"):
            data = _assert_success(
                organizer_client.create_tournament(
                    {
                        "name": f"QA Organizer API {today.isoformat()}",
                        "startDate": today.isoformat(),
                        "endDate": (today + timedelta(days=1)).isoformat(),
                        "status": "draft",
                    }
                )
            )
            tournament_id = _id(data, "tournamentId")
            assert tournament_id
        yield tournament_id
    finally:
        if tournament_id:
            organizer_client.delete_tournament(tournament_id)


@pytest.fixture()
def organizer_category(organizer_client: OrganizerClient, organizer_tournament):
    with allure.step("Crear categoria Organizer"):
        data = _assert_success(
            organizer_client.create_category(
                organizer_tournament,
                {
                    "name": "QA Categoria",
                    "feePerPair": 0,
                    "sortOrder": 1,
                    "qualifiersPerZone": 1,
                },
            )
        )
        category_id = _id(data, "categoryId")
        assert category_id
        return {"tournament_id": organizer_tournament, "category_id": category_id}


def _create_pairs(organizer_client: OrganizerClient, category_id, count=4):
    pair_ids = []
    with allure.step("Crear parejas Organizer"):
        for index in range(1, count + 1):
            data = _assert_success(
                organizer_client.create_pair(
                    category_id,
                    {
                        "player1Name": f"QA Player {index}A",
                        "player2Name": f"QA Player {index}B",
                        "notes": f"QA pair {index}",
                        "timePreferences": [],
                    },
                )
            )
            pair_id = _id(data, "pairId")
            assert pair_id
            pair_ids.append(pair_id)
    return pair_ids


def _create_zone_matches(organizer_client: OrganizerClient, category_id):
    with allure.step("Crear zonas y sortear"):
        _assert_success(organizer_client.create_zones(category_id, {"count": 2}))
        assign = organizer_client.random_assign_zones(category_id, {"numberOfZones": 2})
        assert assign.status_code in (200, 201, 204)

    with allure.step("Generar partidos"):
        data = _assert_success(organizer_client.generate_matches(category_id))
        assert (data.get("totalMatches") or 0) > 0

    zones = _items(_data(organizer_client.list_zones(category_id)))
    matches = []
    for zone in zones:
        zone_id = _id(zone, "zoneId")
        if zone_id:
            matches.extend(_items(_data(organizer_client.list_zone_matches(zone_id))))
    assert matches
    return matches


@allure.feature("Organizer LITE")
@allure.story("Crear torneo")
@pytest.mark.smoke
def test_organizer_create_tournament(organizer_tournament):
    assert organizer_tournament


@allure.feature("Organizer LITE")
@allure.story("Crear categoria")
@pytest.mark.smoke
def test_organizer_create_category(organizer_category):
    assert organizer_category["category_id"]


@allure.feature("Organizer LITE")
@allure.story("Crear parejas")
@pytest.mark.smoke
def test_organizer_create_pairs(organizer_client: OrganizerClient, organizer_category):
    pair_ids = _create_pairs(organizer_client, organizer_category["category_id"])
    assert len(pair_ids) == 4


@allure.feature("Organizer LITE")
@allure.story("Sortear zonas")
@pytest.mark.smoke
def test_organizer_random_assign_zones(organizer_client: OrganizerClient, organizer_category):
    _create_pairs(organizer_client, organizer_category["category_id"])
    with allure.step("Crear zonas requeridas por API actual"):
        _assert_success(organizer_client.create_zones(organizer_category["category_id"], {"count": 2}))
    with allure.step("Sortear zonas random"):
        response = organizer_client.random_assign_zones(organizer_category["category_id"], {"numberOfZones": 2})
        assert response.status_code in (200, 201, 204)
        if response.status_code != 204:
            assert _body(response).get("success", True) is not False


@allure.feature("Organizer LITE")
@allure.story("Generar partidos de zona")
@pytest.mark.smoke
def test_organizer_generate_zone_matches(organizer_client: OrganizerClient, organizer_category):
    _create_pairs(organizer_client, organizer_category["category_id"])
    matches = _create_zone_matches(organizer_client, organizer_category["category_id"])
    assert matches


@allure.feature("Organizer LITE")
@allure.story("Registrar pago manual")
@pytest.mark.smoke
def test_organizer_pair_manual_payment(organizer_client: OrganizerClient, organizer_category):
    pair_id = _create_pairs(organizer_client, organizer_category["category_id"], count=1)[0]
    with allure.step("Registrar pago cash"):
        response = organizer_client.add_pair_payment(pair_id, {"amount": 5000, "method": "cash"})
        assert response.status_code in (200, 201)
        assert _body(response).get("success", True) is not False


@allure.feature("Organizer LITE")
@allure.story("Refund sin nota rechazado")
def test_organizer_refund_without_note_rejected(organizer_client: OrganizerClient, organizer_category):
    pair_id = _create_pairs(organizer_client, organizer_category["category_id"], count=1)[0]
    with allure.step("Intentar refund negativo sin nota"):
        response = organizer_client.add_pair_payment(pair_id, {"amount": -5000, "method": "cash"})
        assert response.status_code == 400
        assert _body(response).get("success", False) is False


@allure.feature("Organizer LITE")
@allure.story("Resultado con mas de 3 sets rechazado")
def test_organizer_result_more_than_three_sets_rejected(organizer_client: OrganizerClient, organizer_category):
    category_id = organizer_category["category_id"]
    _create_pairs(organizer_client, category_id)
    match = _create_zone_matches(organizer_client, category_id)[0]
    match_id = _id(match, "matchId")
    winner_pair_id = match.get("pairAId")
    assert match_id
    assert winner_pair_id

    with allure.step("Intentar cargar resultado con 4 sets"):
        response = organizer_client.set_match_result(
            match_id,
            {
                "winnerPairId": winner_pair_id,
                "sets": [{"a": 6, "b": 0}, {"a": 0, "b": 6}, {"a": 6, "b": 0}, {"a": 6, "b": 0}],
                "walkover": False,
            },
        )
        assert response.status_code == 400
        assert _body(response).get("success", False) is False
