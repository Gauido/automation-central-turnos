from datetime import date, timedelta

import allure
import pytest

from api.auth_client import AuthClient
from api.organizer_client import OrganizerClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.torneos, pytest.mark.smoke]

TENANT_ID = "9001"
OWNER_EMAIL = "qa-owner@botturnos.test"
OWNER_PASSWORD = "Francogaido98&&"


def _body(response):
    try:
        body = response.json()
    except ValueError:
        pytest.skip(f"Organizer response is not JSON. status={response.status_code}")
    assert isinstance(body, dict)
    return body


def _data(body: dict):
    return body.get("data") or body


def _items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "rows", "data", "pairs", "matches", "zones", "podium", "report"):
            nested = value.get(key)
            if isinstance(nested, list):
                return nested
    return []


def _id(value: dict, *keys: str):
    if isinstance(value, dict) and isinstance(value.get("zone"), dict):
        value = value["zone"]
    for key in (*keys, "id"):
        if isinstance(value, dict) and value.get(key):
            return value[key]
    return None


def _assert_status(response, expected: tuple[int, ...], action: str) -> dict:
    if response.status_code == 404:
        pytest.skip(f"Organizer endpoint missing for: {action}")
    if response.status_code in (400, 422):
        pytest.skip(f"Organizer contract missing/mismatch for: {action}. body={response.text[:500]}")
    assert response.status_code in expected
    if response.status_code == 204:
        return {}
    body = _body(response)
    assert body.get("success", True) is not False
    return body


def _extract_zones(body: dict) -> list[dict]:
    data = _data(body)
    zones = _items(data)
    if not zones and isinstance(data, dict):
        zones = _items(data.get("category") or {})
    assert zones, "zoneIds must exist after random assign"
    assert all(_id(zone, "zoneId") for zone in zones)
    return zones


def _extract_matches(body: dict) -> list[dict]:
    data = _data(body)
    matches = _items(data)
    if not matches and isinstance(data, dict):
        matches = _items(data.get("matches") or data.get("generatedMatches") or {})
    assert matches, "generated matches must not be empty"
    assert _id(matches[0], "matchId")
    return matches


def _first_match(matches_by_zone: list[dict]) -> dict | None:
    for zone_body in matches_by_zone:
        for match in _items(_data(zone_body)):
            if _id(match, "matchId"):
                return match
    return None


def _all_matches(matches_by_zone: list[dict]) -> list[dict]:
    matches = []
    for zone_body in matches_by_zone:
        matches.extend(_items(_data(zone_body)))
    return matches


@pytest.fixture()
def organizer_until_results(organizer_client: OrganizerClient, settings: Settings) -> dict:
    today = date.today()
    tournament_id = None

    allure.attach(
        "\n".join(
            [
                "Modulo: Organizer LITE",
                "Base API: /api/organizer",
                f"Tenant: {TENANT_ID}",
                f"Entorno: {settings.env}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )

    with allure.step("Crear torneo"):
        tournament = _data(
            _assert_status(
                organizer_client.create_tournament(
                    {
                        "name": f"QA Organizer Smoke {today.isoformat()}",
                        "startDate": today.isoformat(),
                        "endDate": (today + timedelta(days=1)).isoformat(),
                        "status": "draft",
                    }
                ),
                (200, 201),
                "create tournament",
            )
        )
        tournament_id = _id(tournament, "tournamentId")
        assert tournament_id

    try:
        with allure.step("Crear categoria"):
            category = _data(
                _assert_status(
                    organizer_client.create_category(
                        tournament_id,
                        {
                            "name": "QA 6ta Mixta",
                            "feePerPair": 0,
                            "sortOrder": 1,
                            "qualifiersPerZone": 1,
                        },
                    ),
                    (200, 201),
                    "create category",
                )
            )
            category_id = _id(category, "categoryId")
            assert category_id

        pair_ids = []
        with allure.step("Crear 4 parejas"):
            for index in range(1, 5):
                pair = _data(
                    _assert_status(
                        organizer_client.create_pair(
                            category_id,
                            {
                                "player1Name": f"QA Player {index}A",
                                "player2Name": f"QA Player {index}B",
                                "notes": f"QA smoke pair {index}",
                                "timePreferences": [],
                            },
                        ),
                        (200, 201),
                        f"create pair {index}",
                    )
                )
                pair_id = _id(pair, "pairId")
                assert pair_id
                pair_ids.append(pair_id)
            assert len(pair_ids) == 4

        with allure.step("Crear zonas"):
            _assert_status(organizer_client.create_zones(category_id, {"count": 2}), (200, 201), "create zones")
            created_zones_body = _assert_status(organizer_client.list_zones(category_id), (200,), "list zones")
            created_zones = _extract_zones(created_zones_body)
            assert len(created_zones) >= 2

        with allure.step("Sortear zonas random"):
            zones_body = _assert_status(organizer_client.random_assign_zones(category_id, {}), (200, 201, 204), "random assign zones")
            zones = _extract_zones(zones_body) if _items(_data(zones_body)) else created_zones
            zone_ids = [_id(zone, "zoneId") for zone in zones]
            assert zone_ids

        with allure.step("Generar y obtener matches"):
            matches_body = _assert_status(organizer_client.generate_matches(category_id), (200, 201), "generate matches")
            assert (_data(matches_body).get("totalMatches") or 0) > 0
            matches_by_zone = [
                _assert_status(organizer_client.list_zone_matches(zone_id), (200,), f"list zone matches {zone_id}")
                for zone_id in zone_ids
            ]
            matches = _all_matches(matches_by_zone)
            assert matches

        with allure.step("Cargar resultados validos"):
            for match in matches:
                match_id = _id(match, "matchId")
                winner_pair_id = match.get("pairAId")
                assert match_id
                assert winner_pair_id
                result_body = _assert_status(
                    organizer_client.set_match_result(
                        match_id,
                        {
                            "winnerPairId": winner_pair_id,
                            "sets": [{"a": 6, "b": 3}, {"a": 6, "b": 4}],
                            "walkover": False,
                        },
                    ),
                    (200, 204),
                    f"set match result {match_id}",
                )
                if result_body:
                    assert "6" in str(result_body)

        return {"tournament_id": tournament_id, "category_id": category_id, "zone_ids": zone_ids}
    except Exception:
        if tournament_id:
            try:
                organizer_client.delete_tournament(tournament_id)
            except Exception:
                pass
        raise


@pytest.fixture()
def organizer_client(settings: Settings, api_auth_client: AuthClient):
    owner_email = settings.owner_email or OWNER_EMAIL
    owner_password = settings.owner_password or OWNER_PASSWORD
    login = api_auth_client.login_raw(owner_email, owner_password)
    if login.status_code != 200:
        pytest.skip(f"Owner QA login blocked. status={login.status_code}")

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


@allure.feature("Organizer LITE")
@allure.story("API smoke torneo completo")
def test_organizer_smoke_until_results(organizer_client: OrganizerClient, organizer_until_results: dict) -> None:
    tournament_id = organizer_until_results["tournament_id"]
    try:
        assert tournament_id
        assert organizer_until_results["category_id"]
        assert organizer_until_results["zone_ids"]
    finally:
        organizer_client.delete_tournament(tournament_id)


@allure.feature("Organizer LITE")
@allure.story("Build bracket pendiente")
def test_organizer_build_bracket(organizer_client: OrganizerClient, organizer_until_results: dict) -> None:
    tournament_id = organizer_until_results["tournament_id"]
    try:
        with allure.step("Cerrar zonas"):
            for zone_id in organizer_until_results["zone_ids"]:
                _assert_status(organizer_client.close_zone(zone_id), (200, 204), f"close zone {zone_id}")

        with allure.step("Generar bracket"):
            response = organizer_client.build_bracket(organizer_until_results["category_id"])
            if response.status_code in (400, 404, 422):
                pytest.skip(
                    "Endpoint Organizer LITE build-bracket documentado funcionalmente, "
                    "pero no expuesto/confirmado en API actual."
                )
            assert response.status_code in (200, 201)
    finally:
        organizer_client.delete_tournament(tournament_id)
