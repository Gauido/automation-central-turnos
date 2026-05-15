from collections.abc import Generator
from pathlib import Path
import shutil

import allure
import pytest
from faker import Faker
from playwright.sync_api import Browser, BrowserContext, Page

from api.auth_client import AuthClient
from api.bookings_client import BookingsClient
from api.cash_client import CashClient
from config.settings import Settings, get_settings
from utils.json_reader import read_json
from utils.logger import get_logger


logger = get_logger(__name__)


def _allure_dir(config: pytest.Config) -> Path | None:
    allure_dir = config.getoption("allure_report_dir", default=None) or config.getoption("alluredir", default=None)
    return Path(allure_dir) if allure_dir else None


def pytest_sessionstart(session: pytest.Session) -> None:
    allure_dir = _allure_dir(session.config)
    if not allure_dir or not allure_dir.exists():
        return

    for item in allure_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


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
    return api_auth_client.login(user["email"], user["password"]).access_token


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

    page = item.funcargs.get("page")
    if page is None:
        return

    try:
        artifacts_dir = Path("artifacts/dom")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        safe_name = item.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
        (artifacts_dir / f"{safe_name}.url.txt").write_text(page.url, encoding="utf-8")
        (artifacts_dir / f"{safe_name}.html").write_text(page.content(), encoding="utf-8")

        screenshot = page.screenshot(full_page=True)
        allure.attach(
            screenshot,
            name="failure-screenshot",
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
