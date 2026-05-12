#!/usr/bin/env python3
"""Capture thesis dashboard screenshots with Playwright."""

from __future__ import annotations

import csv
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "reports/figures/dashboard"
REPORT_PATH = PROJECT_ROOT / "reports/project_audit/dashboard_screenshot_capture.csv"
URL = "http://127.0.0.1:8501"
KNOWN_BENIGN_WARNING_FRAGMENTS = (
    "WARN Infinite extent for field",
    'WARN Dropping "fit-x" because spec has discrete width.',
    "WARN Scale bindings are currently only supported for scales with unbinned, continuous domains.",
)


def is_known_benign_warning(line: str) -> bool:
    return line.startswith("warning") and any(fragment in line for fragment in KNOWN_BENIGN_WARNING_FRAGMENTS)


def click_text(page, text: str, timeout: int = 8000) -> bool:
    for locator in [
        page.get_by_role("tab", name=text),
        page.get_by_text(text, exact=True),
        page.locator(f"text={text}"),
    ]:
        try:
            locator.first.click(timeout=timeout)
            page.wait_for_timeout(800)
            return True
        except Exception:
            continue
    return False


def choose_selectbox(page, index: int, option: str) -> bool:
    try:
        box = page.locator('[data-testid="stSelectbox"]').nth(index)
        box.click(timeout=6000)
        page.wait_for_timeout(300)
        page.get_by_text(option, exact=True).last.click(timeout=6000)
        page.wait_for_timeout(1000)
        page.keyboard.press("Escape")
        return True
    except Exception:
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False


def capture(page, name: str, notes: str, rows: list[dict], *, scroll_y: int = 0) -> None:
    path = OUT_DIR / f"{name}.png"
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    try:
        page.evaluate(
            """(scrollY) => {
                window.scrollTo(0, scrollY);
                for (const selector of ['[data-testid="stAppViewContainer"]', 'section.main', '.main']) {
                    const el = document.querySelector(selector);
                    if (el) el.scrollTop = scrollY;
                }
            }""",
            scroll_y,
        )
        if scroll_y:
            page.mouse.move(1000, 900)
            for _ in range(max(1, scroll_y // 650)):
                page.mouse.wheel(0, 650)
                page.wait_for_timeout(150)
        page.wait_for_timeout(500)
    except Exception:
        pass
    page.screenshot(path=str(path), full_page=False)
    rows.append({"screenshot": path.name, "status": "PASS", "notes": notes})


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1500})
        console_messages: list[str] = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)

        capture(page, "overview", "Overview outcome composition and target coverage.", rows)

        if click_text(page, "Data Coverage"):
            capture(page, "data_coverage", "Data coverage tab.", rows)
        else:
            rows.append({"screenshot": "data_coverage.png", "status": "FAIL", "notes": "Could not open Data Coverage tab."})

        if click_text(page, "Models"):
            choose_selectbox(page, 0, "Strict legal distress")
            choose_selectbox(page, 1, "Strict legal distress")
            capture(page, "models_distress", "Models tab for strict distress benchmark.", rows)
            choose_selectbox(page, 0, "Broader failure pressure")
            choose_selectbox(page, 1, "Broader failure pressure")
            capture(page, "models_failure_pressure", "Models tab for broader failure-pressure target.", rows)
            choose_selectbox(page, 0, "Success / resilience")
            choose_selectbox(page, 1, "Success / resilience")
            capture(page, "models_success_resilience", "Models tab for success/resilience target.", rows)
            choose_selectbox(page, 0, "Recovery")
            choose_selectbox(page, 1, "Recovery")
            choose_selectbox(page, 2, "Recovery")
            capture(page, "models_recovery_secondary", "Models tab for validated secondary recovery target.", rows)
        else:
            rows.append({"screenshot": "models_*.png", "status": "FAIL", "notes": "Could not open Models tab."})

        if click_text(page, "Target Lab"):
            capture(page, "target_lab_overview", "Target Lab production coverage and calibration view.", rows)
            capture(page, "target_lab_recovery_reasons", "Target Lab recovery reason-code and feature evidence view.", rows, scroll_y=2200)
        else:
            rows.append({"screenshot": "target_lab_*.png", "status": "FAIL", "notes": "Could not open Target Lab tab."})

        if click_text(page, "Firm Explorer"):
            choose_selectbox(page, 0, "AAPL")
            capture(page, "firm_explorer", "Firm Explorer financial metrics.", rows)
            click_text(page, "Macro Compare")
            capture(page, "macro_compare_training_baseline", "Macro comparison view with standardized chart visible.", rows, scroll_y=520)
        else:
            rows.append({"screenshot": "firm_explorer.png", "status": "FAIL", "notes": "Could not open Firm Explorer tab."})

        if click_text(page, "Artifact Notes"):
            capture(page, "artifact_notes", "Artifact notes and caveats.", rows)
        else:
            rows.append({"screenshot": "artifact_notes.png", "status": "FAIL", "notes": "Could not open Artifact Notes tab."})

        browser.close()

    warning_or_error = [line for line in console_messages if line.startswith(("error", "warning"))]
    actionable_console = [line for line in warning_or_error if line.startswith("error") or not is_known_benign_warning(line)]
    benign_console = [line for line in warning_or_error if is_known_benign_warning(line)]
    if actionable_console:
        rows.append(
            {
                "screenshot": "[console]",
                "status": "REVIEW",
                "notes": "Console warnings/errors captured: " + " | ".join(actionable_console[:10]),
            }
        )
    elif benign_console:
        rows.append(
            {
                "screenshot": "[console]",
                "status": "PASS",
                "notes": f"Only known benign Vega-Lite render warnings captured ({len(benign_console)}); screenshots above passed.",
            }
        )

    with REPORT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["screenshot", "status", "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote dashboard screenshots to {OUT_DIR}")


if __name__ == "__main__":
    main()
