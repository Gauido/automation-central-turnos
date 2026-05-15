import re

from playwright.sync_api import Locator, Page, expect


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, path: str = "/") -> None:
        self.page.goto(path)

    def expect_url_contains(self, value: str) -> None:
        expect(self.page).to_have_url(re.compile(f".*{re.escape(value)}.*"))

    def visible_by_test_id(self, test_id: str) -> Locator:
        locator = self.page.get_by_test_id(test_id)
        expect(locator).to_be_visible()
        return locator

    def fill_first_available(self, selectors: list[str], value: str) -> None:
        locator = self.first_available(selectors)
        locator.fill(value)

    def click_first_available(self, selectors: list[str]) -> None:
        locator = self.first_available(selectors)
        locator.click()

    def first_available(self, selectors: list[str]) -> Locator:
        self.page.wait_for_selector(", ".join(selectors), state="visible")

        for selector in selectors:
            locator = self.page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                return locator
        raise AssertionError(f"No locator found for selectors: {selectors}")
