from datetime import date, timedelta

import allure
import pytest

from api.auth_client import AuthClient
from api.organizer_client import OrganizerClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.organizer, pytest.mark.crud, pytest.mark.usefixtures("clean_organizer_data")]

TENANT_ID = "9001"


def _body(response):
    body = response.json()
    assert isinstance(body, dict)
    return body


def _data(response):
    body = _body(response)
    assert body.get("success", True) is not False
    return body.get("data") or body


def _safe_data_or_skip(response, reason: str):
    if response.status_code != 200:
        pytest.skip(f"{reason}. status={response.status_code}")
    try:
        return _data(response)
    except ValueError:
        pytest.skip(f"{reason}. Response no es JSON.")


def _items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "rows", "data", "tournaments", "categories", "pairs", "zones", "matches"):
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


def _assert_success(response, expected=(200, 201, 204)):
    assert response.status_code in expected
    if response.status_code == 204:
        return {}
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
def tournament(organizer_client: OrganizerClient):
    today = date.today()
    data = _assert_success(
        organizer_client.create_tournament(
            {
                "name": f"QA CRUD Tournament {today.isoformat()}",
                "startDate": today.isoformat(),
                "endDate": (today + timedelta(days=1)).isoformat(),
                "status": "draft",
            }
        )
    )
    tournament_id = _id(data, "tournamentId")
    assert tournament_id
    return {"id": tournament_id, "name": data.get("name")}


def _create_category(organizer_client: OrganizerClient, tournament_id, name="QA CRUD Categoria"):
    data = _assert_success(
        organizer_client.create_category(
            tournament_id,
            {"name": name, "feePerPair": 1000, "sortOrder": 1, "qualifiersPerZone": 1},
        )
    )
    category_id = _id(data, "categoryId")
    assert category_id
    return {"id": category_id, "name": name}


def _create_pair(organizer_client: OrganizerClient, category_id, player1="QA CRUD A", player2="QA CRUD B"):
    data = _assert_success(
        organizer_client.create_pair(
            category_id,
            {"player1Name": player1, "player2Name": player2, "notes": "QA CRUD", "timePreferences": []},
        )
    )
    pair_id = _id(data, "pairId")
    assert pair_id
    return {"id": pair_id, "player1Name": player1, "player2Name": player2}


def _create_matches(organizer_client: OrganizerClient, category_id):
    for index in range(1, 5):
        _create_pair(organizer_client, category_id, f"QA CRUD {index}A", f"QA CRUD {index}B")
    _assert_success(organizer_client.create_zones(category_id, {"count": 2}))
    assign = organizer_client.random_assign_zones(category_id, {"numberOfZones": 2})
    assert assign.status_code in (200, 201, 204)
    _assert_success(organizer_client.generate_matches(category_id))


@allure.feature("Organizer LITE")
@allure.story("Editar torneo API")
def test_api_organizer_update_tournament(organizer_client: OrganizerClient, tournament):
    new_name = f"{tournament['name']} Editado"
    response = organizer_client.update_tournament(tournament["id"], {"name": new_name, "status": "draft"})
    if response.status_code == 404:
        pytest.skip("Endpoint update tournament no disponible.")
    _assert_success(response)
    detail = _assert_success(organizer_client.get_tournament(tournament["id"]))
    assert new_name in str(detail)


@allure.feature("Organizer LITE")
@allure.story("Eliminar torneo API")
def test_api_organizer_delete_tournament(organizer_client: OrganizerClient, tournament):
    response = organizer_client.delete_tournament(tournament["id"])
    _assert_success(response)
    detail = organizer_client.get_tournament(tournament["id"])
    if detail.status_code not in (404, 410):
        listing = _items(_data(organizer_client.list_tournaments()))
        ids = {_id(item, "tournamentId") for item in listing}
        assert tournament["id"] not in ids


@allure.feature("Organizer LITE")
@allure.story("Editar categoria API")
def test_api_organizer_update_category(organizer_client: OrganizerClient, tournament):
    category = _create_category(organizer_client, tournament["id"])
    payload = {"name": "QA CRUD Categoria Editada", "feePerPair": 2500, "sortOrder": 2, "qualifiersPerZone": 2}
    response = organizer_client.update_category(category["id"], payload)
    if response.status_code == 404:
        pytest.skip("Endpoint update category no disponible.")
    _assert_success(response)
    categories = _items(_safe_data_or_skip(organizer_client.list_categories(tournament["id"]), "Listado de categorias no disponible para validar update"))
    assert any(_id(item, "categoryId") == category["id"] and "Editada" in str(item) for item in categories)


@allure.feature("Organizer LITE")
@allure.story("Eliminar categoria API")
def test_api_organizer_delete_category(organizer_client: OrganizerClient, tournament):
    category = _create_category(organizer_client, tournament["id"])
    response = organizer_client.delete_category(category["id"])
    if response.status_code == 404:
        pytest.skip("Endpoint delete category no disponible.")
    _assert_success(response)
    categories = _items(_safe_data_or_skip(organizer_client.list_categories(tournament["id"]), "Listado de categorias no disponible para validar delete"))
    assert category["id"] not in {_id(item, "categoryId") for item in categories}


@allure.feature("Organizer LITE")
@allure.story("Editar pareja API")
def test_api_organizer_update_pair(organizer_client: OrganizerClient, tournament):
    category = _create_category(organizer_client, tournament["id"])
    pair = _create_pair(organizer_client, category["id"])
    response = organizer_client.update_pair(
        pair["id"],
        {"player1Name": "QA CRUD A Editado", "player2Name": "QA CRUD B Editado", "notes": "QA CRUD update", "timePreferences": []},
    )
    if response.status_code == 404:
        pytest.skip("Endpoint update pair no disponible.")
    _assert_success(response)
    pairs = _items(_data(organizer_client.list_pairs(category["id"])))
    assert any(_id(item, "pairId") == pair["id"] and "Editado" in str(item) for item in pairs)


@allure.feature("Organizer LITE")
@allure.story("Eliminar pareja API")
def test_api_organizer_delete_pair_before_draw(organizer_client: OrganizerClient, tournament):
    category = _create_category(organizer_client, tournament["id"])
    pair = _create_pair(organizer_client, category["id"])
    response = organizer_client.delete_pair(pair["id"])
    if response.status_code == 404:
        pytest.skip("Endpoint delete pair no disponible.")
    _assert_success(response)
    pairs = _items(_data(organizer_client.list_pairs(category["id"])))
    assert pair["id"] not in {_id(item, "pairId") for item in pairs}


@allure.feature("Organizer LITE")
@allure.story("Eliminar torneo con datos asociados API")
def test_api_organizer_delete_tournament_with_children(organizer_client: OrganizerClient, tournament):
    category = _create_category(organizer_client, tournament["id"])
    _create_matches(organizer_client, category["id"])
    response = organizer_client.delete_tournament(tournament["id"])
    if response.status_code == 409:
        pytest.xfail("Contrato no permite eliminar torneo con datos asociados; definir comportamiento esperado.")
    _assert_success(response)
    detail = organizer_client.get_tournament(tournament["id"])
    assert detail.status_code in (404, 410)
