import allure
from playwright.sync_api import Page

from utils.web_waits import wait_for_stable_ui


def attach_final_screenshot(page: Page, name: str) -> None:
    wait_for_stable_ui(page)
    allure.attach(
        page.screenshot(full_page=True),
        name=name,
        attachment_type=allure.attachment_type.PNG,
    )
