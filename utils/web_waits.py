from playwright.sync_api import Page, expect


def wait_for_page_ready(page: Page) -> None:
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")


def wait_for_angular_rendered(page: Page) -> None:
    page.wait_for_function(
        """() => {
            const app = document.querySelector('app-root');
            const busy = document.querySelector('.spinner, .loading, [aria-busy="true"]');
            return Boolean(app) && !busy;
        }"""
    )


def wait_for_stable_ui(page: Page) -> None:
    wait_for_page_ready(page)
    wait_for_angular_rendered(page)
    page.wait_for_function(
        """() => new Promise(resolve => {
            requestAnimationFrame(() => requestAnimationFrame(resolve));
        })"""
    )


def expect_ready(page: Page) -> None:
    wait_for_stable_ui(page)
    expect(page.locator("app-root")).to_be_visible()
