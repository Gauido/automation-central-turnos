from datetime import date, timedelta

import allure
import pytest

from api.auth_client import AuthClient
from api.organizer_client import OrganizerClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.organizer, pytest.mark.negative, pytest.mark.usefixtures("clean_organizer_data")]

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
def organizer_category(organizer_client: OrganizerClient):
    today = date.today()
    tournament = _assert_success(
        organizer_client.create_tournament(
            {
                "name": f"QA Organizer Negative {today.isoformat()}",
                "startDate": today.isoformat(),
                "endDate": (today + timedelta(days=1)).isoformat(),
                "status": "draft",
            }
        )
    )
    tournament_id = _id(tournament, "tournamentId")
    assert tournament_id
    category = _assert_success(
        organizer_client.create_category(
            tournament_id,
            {"name": "QA Negativa", "feePerPair": 0, "sortOrder": 1, "qualifiersPerZone": 1},
        )
    )
    category_id = _id(category, "categoryId")
    assert category_id
    return {"tournament_id": tournament_id, "category_id": category_id}


def _create_pairs(organizer_client: OrganizerClient, category_id, count=4):
    pair_ids = []
    for index in range(1, count + 1):
        data = _assert_success(
            organizer_client.create_pair(
                category_id,
                {
                    "player1Name": f"QA Neg Player {index}A",
                    "player2Name": f"QA Neg Player {index}B",
                    "notes": f"QA negative pair {index}",
                    "timePreferences": [],
                },
            )
        )
        pair_ids.append(_id(data, "pairId"))
    assert all(pair_ids)
    return pair_ids


def _create_zone_matches(organizer_client: OrganizerClient, category_id):
    _assert_success(organizer_client.create_zones(category_id, {"count": 2}))
    assign = organizer_client.random_assign_zones(category_id, {"numberOfZones": 2})
    assert assign.status_code in (200, 201, 204)
    data = _assert_success(organizer_client.generate_matches(category_id))
    assert (data.get("totalMatches") or 0) > 0
    zones = _items(_data(organizer_client.list_zones(category_id)))
    matches = []
    for zone in zones:
        zone_id = _id(zone, "zoneId")
        if zone_id:
            matches.extend(_items(_data(organizer_client.list_zone_matches(zone_id))))
    assert zones and matches
    return zones, matches


def _play_all_matches(organizer_client: OrganizerClient, matches):
    for match in matches:
        match_id = _id(match, "matchId")
        winner_pair_id = match.get("pairAId")
        assert match_id and winner_pair_id
        response = organizer_client.set_match_result(
            match_id,
            {"winnerPairId": winner_pair_id, "sets": [{"a": 6, "b": 3}, {"a": 6, "b": 4}], "walkover": False},
        )
        assert response.status_code in (200, 201)


@allure.feature("Organizer LITE")
@allure.story("Refund sin nota rechazado")
def test_organizer_refund_without_note_rejected(organizer_client: OrganizerClient, organizer_category):
    pair_id = _create_pairs(organizer_client, organizer_category["category_id"], count=1)[0]
    assert organizer_client.add_pair_payment(pair_id, {"amount": 5000, "method": "cash"}).status_code in (200, 201)
    response = organizer_client.add_pair_payment(pair_id, {"amount": -5000, "method": "cash"})
    assert response.status_code == 400
    assert _body(response).get("success", False) is False


@allure.feature("Organizer LITE")
@allure.story("Resultado con mas de 3 sets rechazado")
def test_organizer_result_more_than_three_sets_rejected(organizer_client: OrganizerClient, organizer_category):
    category_id = organizer_category["category_id"]
    _create_pairs(organizer_client, category_id)
    _, matches = _create_zone_matches(organizer_client, category_id)
    match = matches[0]
    response = organizer_client.set_match_result(
        _id(match, "matchId"),
        {
            "winnerPairId": match.get("pairAId"),
            "sets": [{"a": 6, "b": 0}, {"a": 0, "b": 6}, {"a": 6, "b": 0}, {"a": 6, "b": 0}],
            "walkover": False,
        },
    )
    assert response.status_code == 400


@allure.feature("Organizer LITE")
@allure.story("Tiebreak invalido rechazado")
def test_organizer_invalid_tiebreak_rejected(organizer_client: OrganizerClient, organizer_category):
    category_id = organizer_category["category_id"]
    _create_pairs(organizer_client, category_id)
    _, matches = _create_zone_matches(organizer_client, category_id)
    match = matches[0]
    response = organizer_client.set_match_result(
        _id(match, "matchId"),
        {"winnerPairId": match.get("pairAId"), "sets": [{"a": 6, "b": 6}], "walkover": False},
    )
    if response.status_code == 200:
        pytest.xfail("Backend acepta tiebreak/set invalido 6-6; esperado HTTP 400.")
    assert response.status_code == 400


@allure.feature("Organizer LITE")
@allure.story("Reabrir zona con bracket rechazado")
def test_organizer_reopen_zone_with_bracket_rejected(organizer_client: OrganizerClient, organizer_category):
    category_id = organizer_category["category_id"]
    _create_pairs(organizer_client, category_id)
    zones, matches = _create_zone_matches(organizer_client, category_id)
    _play_all_matches(organizer_client, matches)
    for zone in zones:
        response = organizer_client.close_zone(_id(zone, "zoneId"))
        assert response.status_code in (200, 201, 204)
    bracket = organizer_client.build_bracket(category_id)
    if bracket.status_code == 404:
        pytest.skip("Endpoint build-bracket Organizer no disponible para validar reopen con bracket.")
    assert bracket.status_code in (200, 201)
    response = organizer_client.reopen_zone(_id(zones[0], "zoneId"))
    assert response.status_code == 409


@allure.feature("Organizer LITE")
@allure.story("Remover pareja con partido jugado rechazado")
def test_organizer_remove_pair_with_played_match_rejected(organizer_client: OrganizerClient, organizer_category):
    category_id = organizer_category["category_id"]
    _create_pairs(organizer_client, category_id)
    zones, matches = _create_zone_matches(organizer_client, category_id)
    match = matches[0]
    pair_id = match.get("pairAId")
    zone_id = _id(zones[0], "zoneId")
    response = organizer_client.set_match_result(
        _id(match, "matchId"),
        {"winnerPairId": pair_id, "sets": [{"a": 6, "b": 3}, {"a": 6, "b": 4}], "walkover": False},
    )
    assert response.status_code in (200, 201)
    response = organizer_client.remove_pair_from_zone(zone_id, pair_id)
    assert response.status_code == 409
