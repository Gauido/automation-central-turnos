import allure
import pytest

from api.auth_client import AuthClient
from api.tenant_modules_client import TenantModulesClient
from config.settings import Settings


pytestmark = [pytest.mark.api, pytest.mark.suscripcion, pytest.mark.smoke]

TENANT_ID = 9001
NON_CRITICAL_MODULES = ("marketing", "predictions", "reports", "organizer")
CRITICAL_MODULES = {"bookings", "reservas"}


def _data(response):
    assert response.status_code == 200
    body = response.json()
    assert body.get("success", True) is not False
    return body.get("data") or body


def _items(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "rows", "data", "modules", "tenantModules"):
            nested = value.get(key)
            if isinstance(nested, list):
                return nested
    return []


def _module_key(module: dict) -> str | None:
    return module.get("moduleKey") or module.get("key") or module.get("name")


def _module_enabled(module: dict) -> bool:
    return bool(module.get("enabled", module.get("isEnabled", False)))


def _pick_module(modules: list[dict]) -> tuple[str, bool]:
    for preferred in NON_CRITICAL_MODULES:
        for module in modules:
            if _module_key(module) == preferred:
                return preferred, _module_enabled(module)
    for module in modules:
        key = _module_key(module)
        if key and key not in CRITICAL_MODULES:
            return key, _module_enabled(module)
    pytest.skip("No hay modulo no critico detectable para toggle seguro.")


@pytest.fixture()
def tenant_modules_admin(settings: Settings, api_token: str):
    client = TenantModulesClient(
        str(settings.api_base_url),
        settings.api_timeout_seconds,
        verify=not settings.ignore_https_errors,
    )
    client.set_bearer_token(api_token)
    yield client
    client.close()


@pytest.fixture()
def tenant_modules_owner(settings: Settings, api_auth_client: AuthClient):
    if not settings.owner_email or not settings.owner_password:
        pytest.skip("Owner credentials no configuradas en entorno local.")
    login = api_auth_client.login_raw(settings.owner_email, settings.owner_password)
    if login.status_code != 200:
        pytest.skip(f"Owner login blocked. status={login.status_code}")
    body = login.json()
    token = (body.get("data") or {}).get("token") or body.get("accessToken") or body.get("token") or body.get("jwt")
    assert token
    client = TenantModulesClient(
        str(settings.api_base_url),
        settings.api_timeout_seconds,
        verify=not settings.ignore_https_errors,
    )
    client.set_bearer_token(token)
    client.set_tenant(str(TENANT_ID))
    yield client
    client.close()


@allure.feature("Tenant Modules")
@allure.story("Smoke toggle modulo no critico")
def test_api_tenant_modules_smoke(tenant_modules_admin: TenantModulesClient, tenant_modules_owner: TenantModulesClient):
    allure.attach(
        "\n".join(
            [
                "Contrato real Swagger: /api/admin/tenant-modules",
                f"Tenant: {TENANT_ID}",
            ]
        ),
        name="Datos del test",
        attachment_type=allure.attachment_type.TEXT,
    )

    tenants = _data(tenant_modules_admin.list_tenants())
    assert tenants

    modules = _items(_data(tenant_modules_admin.tenant_modules(TENANT_ID)))
    assert modules
    module_key, original_enabled = _pick_module(modules)

    try:
        off = tenant_modules_admin.set_module(TENANT_ID, module_key, False)
        assert off.status_code == 200
        owner_modules = _data(tenant_modules_owner.my_modules())
        assert owner_modules
    finally:
        restore = tenant_modules_admin.set_module(TENANT_ID, module_key, original_enabled)
        assert restore.status_code == 200
