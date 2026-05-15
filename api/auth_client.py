from dataclasses import dataclass

from api.base_client import BaseClient


@dataclass(frozen=True)
class LoginResponse:
    access_token: str
    raw: dict


class AuthClient(BaseClient):
    login_path = "/api/auth/login"

    def login(self, email: str, password: str) -> LoginResponse:
        payload = {
            "email": email,
            "password": password,
        }

        response = self.post(self.login_path, json=payload)
        assert response.status_code == 200
        body = response.json()
        data = body.get("data") or {}
        token = data.get("token") or body.get("accessToken") or body.get("token") or body.get("jwt")

        if not token:
            raise AssertionError(f"Login response does not include an access token. Body keys: {body.keys()}")

        return LoginResponse(access_token=token, raw=body)

    def login_raw(self, email: str, password: str):
        return self.post(self.login_path, json={"email": email, "password": password})
