from collections.abc import Callable
from dataclasses import dataclass

from playwright.sync_api import Browser, BrowserContext, Page


@dataclass
class WebActor:
    context: BrowserContext
    page: Page

    def close(self) -> None:
        self.context.close()


def create_web_actors(browser: Browser, browser_context_args: dict, count: int = 2) -> list[WebActor]:
    actors = []
    for _ in range(count):
        context = browser.new_context(**browser_context_args)
        actors.append(WebActor(context=context, page=context.new_page()))
    return actors


def close_web_actors(actors: list[WebActor]) -> None:
    for actor in actors:
        actor.close()


def run_booking_attempts(actors: list[WebActor], attempt: Callable[[Page], object]) -> list[object]:
    return [attempt(actor.page) for actor in actors]
