"""Non-functional checks for Automation Quest expectations (web).

These checks are intentionally lightweight and stable enough for hackathon runs.
"""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import pytest

from src.utils.config import ConfigLoader
from src.utils.logger import StructuredLogger

logger = StructuredLogger.get_logger(__name__)


pytestmark = [
    pytest.mark.web,
    pytest.mark.live,
    pytest.mark.integration,
    pytest.mark.nonfunctional,
]


class TestNonFunctionalWeb:
    """Basic accessibility, performance, security, and visual checks."""

    def test_security_https_and_response(self, driver, event_loop):
        if driver.is_mobile:
            pytest.skip("Security web check is web-only")

        page = driver.get_page()
        response = event_loop.run_until_complete(
            page.goto(ConfigLoader.base_url().strip(), wait_until="domcontentloaded")
        )
        assert page.url.startswith("https://"), f"Expected HTTPS URL, got: {page.url}"
        assert response is not None, "No HTTP response object from navigation"
        assert response.status < 500, f"Server error status: {response.status}"

    def test_performance_domcontentloaded_under_budget(self, driver, event_loop):
        if driver.is_mobile:
            pytest.skip("Performance web check is web-only")

        page = driver.get_page()
        url = ConfigLoader.base_url().strip()

        start = perf_counter()
        event_loop.run_until_complete(page.goto(url, wait_until="domcontentloaded"))
        elapsed = perf_counter() - start

        # Keep budget realistic for live staging and CI variability.
        assert elapsed < 20.0, f"domcontentloaded took too long: {elapsed:.2f}s"

    def test_accessibility_landmarks_present(self, driver, event_loop):
        if driver.is_mobile:
            pytest.skip("Accessibility web check is web-only")

        page = driver.get_page()
        event_loop.run_until_complete(page.goto(ConfigLoader.base_url().strip(), wait_until="domcontentloaded"))

        has_main = event_loop.run_until_complete(page.locator("main, [role='main']").first.count()) > 0
        heading_count = event_loop.run_until_complete(page.locator("h1, h2").count())

        assert has_main, "No main landmark detected"
        assert heading_count > 0, "No primary headings detected"

    def test_visual_snapshot_generated(self, driver, event_loop):
        if driver.is_mobile:
            pytest.skip("Visual web check is web-only")

        page = driver.get_page()
        event_loop.run_until_complete(page.goto(ConfigLoader.base_url().strip(), wait_until="domcontentloaded"))

        screenshots_dir = Path(ConfigLoader.screenshots_dir())
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        target = screenshots_dir / "nonfunctional_homepage.png"

        event_loop.run_until_complete(page.screenshot(path=str(target), full_page=True))
        assert target.exists(), "Visual snapshot not created"
        assert target.stat().st_size > 0, "Visual snapshot file is empty"

        logger.info("Non-functional visual snapshot saved: %s", target)
