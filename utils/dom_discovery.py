from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import allure
from playwright.sync_api import Page

from utils.report_config import is_debug_report


ARTIFACTS_DIR = Path("artifacts/dom")
SCREENSHOTS_DIR = Path("screenshots")


def discover_dom(page: Page, name: str, root_selector: str | None = None, html_limit: int = 200_000) -> dict[str, Any]:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    screenshot_path = SCREENSHOTS_DIR / f"{name}.png"
    screenshot = page.screenshot(path=str(screenshot_path), full_page=True)

    data = _extract_dom_data(page, root_selector=root_selector, html_limit=html_limit)
    markdown = _to_markdown(data, root_selector=root_selector)

    allure.attach(screenshot, name=f"{name}.png", attachment_type=allure.attachment_type.PNG)

    artifacts = {"screenshot": str(screenshot_path)}
    if is_debug_report():
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        html_path = ARTIFACTS_DIR / f"{name}.html"
        diagnostics_path = ARTIFACTS_DIR / f"{name}-diagnostics.md"
        json_path = ARTIFACTS_DIR / f"{name}-diagnostics.json"

        html_path.write_text(data["html"], encoding="utf-8")
        diagnostics_path.write_text(markdown, encoding="utf-8")
        json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

        allure.attach(data["html"], name=f"{name}.html", attachment_type=allure.attachment_type.HTML)
        allure.attach(markdown, name=f"{name}-diagnostics.md", attachment_type=allure.attachment_type.TEXT)
        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False),
            name=f"{name}-diagnostics.json",
            attachment_type=allure.attachment_type.JSON,
        )
        artifacts.update(
            {
                "html": str(html_path),
                "diagnostics": str(diagnostics_path),
                "json": str(json_path),
            }
        )

    return {
        **data,
        "artifacts": artifacts,
    }


def _extract_dom_data(page: Page, root_selector: str | None, html_limit: int) -> dict[str, Any]:
    return page.evaluate(
        """({ rootSelector, htmlLimit }) => {
            const root = rootSelector ? document.querySelector(rootSelector) : document.body;
            const scope = root || document.body;
            const isVisible = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
            const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
            const attrs = (el) => ({
                tag: el.tagName.toLowerCase(),
                text: clean(el.innerText || el.value || '').slice(0, 180),
                role: el.getAttribute('role'),
                ariaLabel: el.getAttribute('aria-label'),
                placeholder: el.getAttribute('placeholder'),
                testId: el.getAttribute('data-testid'),
                id: el.id || null,
                name: el.getAttribute('name'),
                type: el.getAttribute('type'),
                href: el.getAttribute('href'),
                className: typeof el.className === 'string' ? el.className.slice(0, 160) : null,
                visible: isVisible(el),
            });
            const collect = (selector) => Array.from(scope.querySelectorAll(selector)).filter(isVisible).map(attrs);
            const visibleText = clean(scope.innerText).slice(0, 4000);
            const roleElements = Array.from(scope.querySelectorAll('[role]')).filter(isVisible).map(attrs);
            const tabs = Array.from(scope.querySelectorAll('[role="tab"], [aria-selected], button[class*="tab"], button[class*="seg"]'))
                .filter(isVisible)
                .map(attrs);

            return {
                url: window.location.href,
                title: document.title,
                rootSelector,
                visibleText,
                headings: collect('h1, h2, h3, h4, h5, h6, [role="heading"]'),
                buttons: collect('button, input[type="button"], input[type="submit"]'),
                links: collect('a[href]'),
                inputs: collect('input'),
                textareas: collect('textarea'),
                selects: collect('select, [role="combobox"], app-custom-select'),
                roleElements,
                ariaLabels: collect('[aria-label]'),
                placeholders: collect('[placeholder]'),
                testIds: collect('[data-testid]'),
                tabs,
                dialogs: collect('[role="dialog"], dialog, .modal, .modal-container, mat-dialog-container'),
                html: scope.outerHTML.slice(0, htmlLimit),
                counts: {
                    headings: collect('h1, h2, h3, h4, h5, h6, [role="heading"]').length,
                    buttons: collect('button, input[type="button"], input[type="submit"]').length,
                    links: collect('a[href]').length,
                    inputs: collect('input').length,
                    textareas: collect('textarea').length,
                    selects: collect('select, [role="combobox"], app-custom-select').length,
                    roles: roleElements.length,
                    ariaLabels: collect('[aria-label]').length,
                    placeholders: collect('[placeholder]').length,
                    testIds: collect('[data-testid]').length,
                    tabs: tabs.length,
                    dialogs: collect('[role="dialog"], dialog, .modal, .modal-container, mat-dialog-container').length,
                },
            };
        }""",
        {"rootSelector": root_selector, "htmlLimit": html_limit},
    )


def _to_markdown(data: dict[str, Any], root_selector: str | None) -> str:
    lines = [
        f"# DOM Discovery: {root_selector or 'document.body'}",
        "",
        f"- URL: `{data['url']}`",
        f"- Title: `{data['title']}`",
        f"- Root selector: `{root_selector or 'document.body'}`",
        "",
        "## Counts",
    ]
    for key, value in data["counts"].items():
        lines.append(f"- {key}: {value}")

    sections = [
        ("Headings", "headings"),
        ("Buttons", "buttons"),
        ("Links", "links"),
        ("Inputs", "inputs"),
        ("Textareas", "textareas"),
        ("Selects", "selects"),
        ("Role Elements", "roleElements"),
        ("Aria Labels", "ariaLabels"),
        ("Placeholders", "placeholders"),
        ("Data Test IDs", "testIds"),
        ("Tabs", "tabs"),
        ("Dialogs", "dialogs"),
    ]
    for title, key in sections:
        lines.extend(["", f"## {title}"])
        items = data.get(key) or []
        if not items:
            lines.append("- None")
            continue
        for item in items[:80]:
            summary = _element_summary(item)
            lines.append(f"- {summary}")

    lines.extend(["", "## Visible Text Sample", "", "```text", data.get("visibleText", "")[:2000], "```"])
    return "\n".join(lines)


def _element_summary(item: dict[str, Any]) -> str:
    parts = [item.get("tag") or "?"]
    for key in ("role", "testId", "ariaLabel", "placeholder", "id", "name", "type", "href"):
        value = item.get(key)
        if value:
            parts.append(f'{key}="{value}"')
    text = item.get("text")
    if text:
        parts.append(f'text="{text}"')
    return " ".join(parts)
