import allure
import pytest

from api.auth_client import AuthClient


pytestmark = [pytest.mark.api, pytest.mark.auth, pytest.mark.smoke]


@allure.feature("API Auth")
@allure.story("Login exitoso")
def test_api_login_success(api_auth_client: AuthClient, api_users: dict) -> None:
    user = api_users["users"]["super_admin"]
    response = api_auth_client.login(user["email"], user["password"])

    assert response.access_token
    assert response.raw["success"] is True
    assert response.raw["data"]["email"] == user["email"]


@allure.feature("API Auth")
@allure.story("Login con credenciales invalidas")
def test_api_login_invalid_credentials(api_auth_client: AuthClient, api_users: dict) -> None:
    user = api_users["users"]["super_admin"]
    response = api_auth_client.login_raw(user["email"], "Wrong1234")

    assert response.status_code == 401
    assert response.json()["success"] is False
