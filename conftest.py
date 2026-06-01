from collections.abc import Generator
from datetime import datetime
import json
from pathlib import Path
import shutil

import allure
import pytest
from faker import Faker
from playwright.sync_api import Browser, BrowserContext, Page

from api.auth_client import AuthClient
from api.bookings_client import BookingsClient
from api.cash_client import CashClient
from api.qa_client import QaClient
from config.settings import Settings, get_settings
from utils.json_reader import read_json
from utils.logger import get_logger
from utils.test_context_reporter import attach_test_context


logger = get_logger(__name__)
ARTIFACTS_DIR = Path("artifacts/dom")


def _allure_dir(config: pytest.Config) -> Path | None:
    allure_dir = config.getoption("allure_report_dir", default=None) or config.getoption("alluredir", default=None)
    return Path(allure_dir) if allure_dir else None


def _mask_text(value: str) -> str:
    return value.replace(get_settings().qa_token or "", "***")


def pytest_sessionstart(session: pytest.Session) -> None:
    allure_dir = _allure_dir(session.config)
    if not allure_dir:
        return

    allure_dir.mkdir(parents=True, exist_ok=True)

    for item in allure_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    settings = get_settings()
    (allure_dir / "environment.properties").write_text(
        "\n".join(
            [
                f"env={settings.env}",
                f"web_base_url={settings.web_base_url}",
                f"api_base_url={settings.api_base_url}",
                f"qa_api_base_url={settings.qa_api_base_url or ''}",
            ]
        ),
        encoding="utf-8",
    )
    (allure_dir / "categories.json").write_text(
        json.dumps(
            [
                {"name": "Product defect", "matchedStatuses": ["failed"]},
                {"name": "Test defect", "matchedStatuses": ["broken"]},
                {"name": "Skipped - missing QA data", "matchedStatuses": ["skipped"], "messageRegex": ".*Falta.*|.*Missing.*"},
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def _organizer_test_type(node: pytest.Item) -> str:
    if "web" in {marker.name for marker in node.iter_markers()}:
        return "web"
    if "api" in {marker.name for marker in node.iter_markers()}:
        return "api"
    return "unknown"


def _organizer_created_data(nodeid: str) -> dict:
    data: dict = {}
    if "create_tournament" in nodeid or "smoke" in nodeid or "flow" in nodeid:
        data["torneo"] = "QA_AUTO_Organizer_*"
    if "category" in nodeid or "pairs" in nodeid or "zones" in nodeid or "match" in nodeid or "report" in nodeid:
        data["categoria"] = "QA Categoria*"
    if "pairs" in nodeid or "zones" in nodeid or "match" in nodeid or "report" in nodeid:
        data["parejas"] = 4
    if "zones" in nodeid or "match" in nodeid or "report" in nodeid:
        data["zonas"] = 2
    return data


def _organizer_endpoints(nodeid: str) -> list[str]:
    endpoints = []
    if "test_api_organizer" in nodeid:
        endpoints.extend(
            [
                "POST /api/organizer/tournaments",
                "POST /api/organizer/tournaments/{id}/categories",
                "POST /api/organizer/categories/{cid}/pairs",
                "POST /api/organizer/categories/{cid}/zones",
                "POST /api/organizer/categories/{cid}/zones/random-assign",
                "POST /api/organizer/categories/{cid}/zones/generate-matches",
            ]
        )
    if "cleanup_organizer" in nodeid:
        endpoints.append("POST /api/qa/cleanup/organizer")
    return endpoints


def _attach_organizer_test_context(item: pytest.Item) -> None:
    markers = sorted(marker.name for marker in item.iter_markers())
    if "organizer" not in markers:
        return

    settings = get_settings()
    test_type = _organizer_test_type(item)
    browser = item.funcargs.get("browser_name") if test_type == "web" else None
    headed = bool(item.config.getoption("--headed"))
    cleanup_enabled = "clean_organizer_data" in getattr(item, "fixturenames", ())
    if item.get_closest_marker("usefixtures"):
        cleanup_enabled = cleanup_enabled or "clean_organizer_data" in item.get_closest_marker("usefixtures").args

    context = {
        "contexto": {
            "ambiente": str(settings.env).upper(),
            "modulo": "Organizer LITE",
            "tipo_test": test_type,
            "browser": browser,
            "modo_ejecucion": "headed" if headed else "headless",
            "base_url": str(settings.web_base_url),
            "api_base_url": str(settings.api_base_url),
        },
        "usuario": {
            "rol": "owner",
            "email": settings.owner_email,
        },
        "tenant": {
            "id": 9001,
        },
        "datos_creados": _organizer_created_data(item.nodeid),
        "cleanup": {
            "endpoint": "POST /api/qa/cleanup/organizer",
            "antes_del_test": cleanup_enabled,
            "despues_del_test": cleanup_enabled,
        },
        "extra": {
            "nodeid": item.nodeid,
            "markers": markers,
            "endpoints_principales": _organizer_endpoints(item.nodeid),
        },
    }
    attach_test_context(**context)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item: pytest.Item) -> None:
    _attach_organizer_test_context(item)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def fake() -> Faker:
    return Faker("es_AR")


@pytest.fixture(scope="session")
def web_users() -> dict:
    return read_json("tests/web/data/web_users.json")


@pytest.fixture(scope="session")
def web_booking() -> dict:
    return read_json("tests/web/data/web_booking.json")


@pytest.fixture(scope="session")
def web_courts() -> dict:
    return read_json("tests/web/data/web_courts.json")


@pytest.fixture(scope="session")
def api_users() -> dict:
    return read_json("tests/api/data/api_users.json")


@pytest.fixture(scope="session")
def api_booking() -> dict:
    return read_json("tests/api/data/api_booking.json")


@pytest.fixture(scope="session")
def api_tenants() -> dict:
    return read_json("tests/api/data/api_tenants.json")


@pytest.fixture(scope="session")
def e2e_users() -> dict:
    return read_json("tests/e2e/data/e2e_users.json")


@pytest.fixture(scope="session")
def api_auth_client(settings: Settings) -> Generator[AuthClient, None, None]:
    client = AuthClient(
        base_url=str(settings.api_base_url),
        timeout=settings.api_timeout_seconds,
        verify=not settings.ignore_https_errors,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def api_token(api_auth_client: AuthClient, api_users: dict) -> str:
    user = api_users["users"]["super_admin"]
    previous = api_auth_client.reporting_enabled
    api_auth_client.reporting_enabled = False
    try:
        return api_auth_client.login(user["email"], user["password"]).access_token
    finally:
        api_auth_client.reporting_enabled = previous


@pytest.fixture()
def bookings_client(settings: Settings, api_token: str) -> Generator[BookingsClient, None, None]:
    client = BookingsClient(str(settings.api_base_url), settings.api_timeout_seconds, verify=not settings.ignore_https_errors)
    client.set_bearer_token(api_token)
    yield client
    client.close()


@pytest.fixture()
def cash_client(settings: Settings, api_token: str, api_booking: dict) -> Generator[CashClient, None, None]:
    client = CashClient(str(settings.api_base_url), settings.api_timeout_seconds, verify=not settings.ignore_https_errors)
    client.set_bearer_token(api_token)
    client.set_tenant(api_booking["tenant_id"])
    yield client
    client.close()


@pytest.fixture(scope="session")
def qa_client(settings: Settings) -> Generator[QaClient, None, None]:
    if not settings.qa_api_base_url:
        pytest.skip("Missing QA_API_BASE_URL in .env")
    if not settings.qa_token:
        pytest.skip("Missing QA_TOKEN in .env")

    client = QaClient(
        str(settings.qa_api_base_url),
        settings.qa_token,
        settings.api_timeout_seconds,
        verify=not settings.ignore_https_errors,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
def qa_test_data(qa_client: QaClient) -> dict:
    response = qa_client.get_silent("/test-data")
    if response.status_code != 200:
        pytest.skip("QA test-data endpoint not available")
    body = response.json()
    return body.get("data") or body


@pytest.fixture()
def clean_organizer_data(qa_client: QaClient) -> Generator[None, None, None]:
    qa_client.cleanup_organizer()
    yield
    qa_client.cleanup_organizer()


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: pytest.Config) -> dict:
    launch_args = {}
    if pytestconfig.getoption("--headed"):
        launch_args["headless"] = False
        launch_args["args"] = ["--start-maximized"]
    return launch_args


@pytest.fixture()
def browser_context_args(browser_context_args: dict, settings: Settings, pytestconfig: pytest.Config) -> dict:
    context_args = {
        **browser_context_args,
        "base_url": str(settings.web_base_url),
        "ignore_https_errors": settings.ignore_https_errors,
    }
    if pytestconfig.getoption("--headed"):
        context_args["viewport"] = None
        context_args["no_viewport"] = True
    else:
        context_args["viewport"] = {"width": 1440, "height": 900}
    return context_args


@pytest.fixture()
def context(browser: Browser, browser_context_args: dict) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(**browser_context_args)
    context.set_default_timeout(browser_context_args.get("default_timeout", 30000))
    yield context
    context.close()


@pytest.fixture()
def page(context: BrowserContext, pytestconfig: pytest.Config) -> Generator[Page, None, None]:
    page = context.new_page()
    if pytestconfig.getoption("--headed"):
        page.evaluate(
            """() => {
                window.moveTo(0, 0);
                window.resizeTo(screen.availWidth, screen.availHeight);
            }"""
        )
    yield page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    error_data = {
        "nodeid": item.nodeid,
        "phase": report.when,
        "outcome": report.outcome,
        "message": _mask_text(str(report.longrepr))[:2000],
    }
    allure.attach(
        json.dumps(error_data, indent=2, ensure_ascii=False),
        name="error.json",
        attachment_type=allure.attachment_type.JSON,
    )

    page = item.funcargs.get("page")
    if page is None:
        return

    try:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_name = f"{timestamp}_{safe_name}"
        (ARTIFACTS_DIR / f"{artifact_name}.url.txt").write_text(page.url, encoding="utf-8")
        (ARTIFACTS_DIR / f"{artifact_name}.html").write_text(page.content(), encoding="utf-8")

        screenshot = page.screenshot(full_page=True)
        allure.attach(
            screenshot,
            name=f"{artifact_name}.png",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as exc:  # pragma: no cover - best effort diagnostic hook
        logger.warning("Could not attach failure screenshot: %s", exc)


def pytest_sessionfinish(session: pytest.Session) -> None:
    session.config._keep_allure_containers = session.testsfailed > 0


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config: pytest.Config) -> None:
    if getattr(config, "_keep_allure_containers", True):
        return

    allure_dir = _allure_dir(config)
    if not allure_dir:
        return

    for container_file in allure_dir.glob("*-container.json"):
        container_file.unlink(missing_ok=True)
