"""pytest configuration and fixtures for Gajab automation framework.

Provides:
- Session-scoped fixtures for isMobile flag (read once)
- Function-scoped fixtures for driver (new driver per test)
- Page factory fixture
- Test start/end logging
- Failure hook for centralized screenshot/diagnostic capture
"""

import pytest
import asyncio
import time
import os
import re
from datetime import datetime
from pathlib import Path
from html import escape

from src.utils.config import ConfigLoader
from src.utils.logger import StructuredLogger
from src.fixtures.driver_factory import DriverFactory
from src.fixtures.page_factory import PageObjectFactory

logger = StructuredLogger.get_logger(__name__)


def _build_run_artifact_paths() -> dict:
    """Create unique artifact directories and file paths for this pytest run."""
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path("reports") / "runs" / run_id
    screenshots_dir = run_dir / "screenshots"
    allure_dir = run_dir / "allure-results"
    traces_dir = run_dir / "playwright-traces"

    run_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    allure_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "html": str(run_dir / "report.html"),
        "junit": str(run_dir / "junit.xml"),
        "json": str(run_dir / "report.json"),
        "allure": str(allure_dir),
        "screenshots": str(screenshots_dir),
        "traces": str(traces_dir),
        "dashboard": str(run_dir / "index.html"),
    }


def _sanitize_filename(value: str) -> str:
    """Make a safe filename from a pytest node/test name."""
    return re.sub(r"[^a-zA-Z0-9._-]", "_", value)


def _write_run_dashboard(artifacts: dict, counts: dict, duration_sec: float, exit_code: int) -> None:
    """Write a human-friendly dashboard for each run with direct artifact links."""
    status = "PASS" if exit_code == 0 else "FAIL"
    status_class = "pass" if exit_code == 0 else "fail"

    html_content = f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Automation Run Dashboard</title>
    <style>
        :root {{
            --bg: #f3f5f7;
            --card: #ffffff;
            --ink: #16202a;
            --muted: #5d6b7a;
            --line: #d9e0e7;
            --accent: #0078d4;
            --ok: #107c10;
            --bad: #d13438;
        }}
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; font-family: Segoe UI, Tahoma, sans-serif; background: linear-gradient(135deg, #eef6ff 0%, var(--bg) 55%, #f9f6ef 100%); color: var(--ink); }}
        .wrap {{ max-width: 980px; margin: 28px auto; padding: 0 16px; }}
        .hero {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 20px; box-shadow: 0 8px 20px rgba(0,0,0,.04); }}
        .title {{ margin: 0 0 8px; font-size: 28px; line-height: 1.2; }}
        .sub {{ margin: 0; color: var(--muted); }}
        .badge {{ display: inline-block; margin-top: 12px; padding: 6px 10px; border-radius: 999px; font-weight: 700; letter-spacing: .3px; color: #fff; }}
        .badge.pass {{ background: var(--ok); }}
        .badge.fail {{ background: var(--bad); }}
        .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); margin-top: 14px; }}
        .stat {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }}
        .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }}
        .value {{ margin-top: 6px; font-size: 24px; font-weight: 700; }}
        .links {{ margin-top: 16px; display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
        a.card {{ text-decoration: none; color: var(--ink); background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; display: block; transition: transform .15s ease, box-shadow .15s ease; }}
        a.card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 16px rgba(0,0,0,.06); border-color: #bfd6ea; }}
        .k {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .4px; }}
        .v {{ margin-top: 6px; font-weight: 600; }}
        .hint {{ margin-top: 16px; color: var(--muted); font-size: 13px; }}
        code {{ background: #eef1f5; padding: 1px 6px; border-radius: 6px; }}
    </style>
</head>
<body>
    <main class=\"wrap\">
        <section class=\"hero\">
            <h1 class=\"title\">Automation Run Dashboard</h1>
            <p class=\"sub\">Run ID: {escape(artifacts['run_id'])}</p>
            <span class=\"badge {status_class}\">{status}</span>
            <div class=\"grid\">
                <div class=\"stat\"><div class=\"label\">Collected</div><div class=\"value\">{counts['collected']}</div></div>
                <div class=\"stat\"><div class=\"label\">Passed</div><div class=\"value\">{counts['passed']}</div></div>
                <div class=\"stat\"><div class=\"label\">Failed</div><div class=\"value\">{counts['failed']}</div></div>
                <div class=\"stat\"><div class=\"label\">Skipped</div><div class=\"value\">{counts['skipped']}</div></div>
                <div class=\"stat\"><div class=\"label\">Duration</div><div class=\"value\">{duration_sec:.2f}s</div></div>
            </div>
            <div class=\"links\">
                <a class=\"card\" href=\"report.html\"><div class=\"k\">Human Report</div><div class=\"v\">pytest HTML report</div></a>
                <a class=\"card\" href=\"junit.xml\"><div class=\"k\">CI Report</div><div class=\"v\">JUnit XML</div></a>
                <a class=\"card\" href=\"report.json\"><div class=\"k\">Machine Report</div><div class=\"v\">JSON summary</div></a>
                <a class=\"card\" href=\"allure-results/\"><div class=\"k\">Allure Data</div><div class=\"v\">Raw allure results</div></a>
                <a class=\"card\" href=\"screenshots/\"><div class=\"k\">Failure Evidence</div><div class=\"v\">Screenshots</div></a>
                <a class=\"card\" href=\"playwright-traces/\"><div class=\"k\">Playwright Native</div><div class=\"v\">Trace ZIP files</div></a>
            </div>
            <p class=\"hint\">Open any trace ZIP with Playwright Trace Viewer: <code>playwright show-trace &lt;trace.zip&gt;</code></p>
        </section>
    </main>
</body>
</html>
"""

    Path(artifacts["dashboard"]).write_text(html_content, encoding="utf-8")


# ===== EVENT LOOP FIXTURE =====

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async fixtures."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# ===== PLATFORM FLAG FIXTURE =====

@pytest.fixture(scope="session")
def is_mobile(request):
    """
    Read isMobile flag once per session (immutable thereafter).
    
    Source of truth (only place read):
    1. Environment variable IS_MOBILE=true|false
    2. CLI argument --isMobile
    3. Default: false (Web mode)
    
    This fixture ensures the flag is read exactly ONCE and cached.
    All driver and page factory decisions branch on this value.
    """
    # Check CLI argument first
    flag = request.config.getoption("--isMobile", default=False)
    
    # If no CLI arg, check environment variable
    if not flag:
        flag = ConfigLoader.is_mobile()
    
    # Log platform selection prominently
    platform = "MOBILE (Appium/Android)" if flag else "WEB (Playwright)"
    print("\n" + "=" * 70)
    print(f"FRAMEWORK RUNNING IN {platform} MODE")
    print("=" * 70 + "\n")
    
    logger.info(f"Session platform: isMobile={flag} ({platform})")
    
    return flag


# ===== DRIVER FIXTURE =====

@pytest.fixture
def driver(is_mobile, event_loop, request):
    """
    Provide driver to test — Web (Playwright) or Mobile (Appium).
    
    Driver selection based on isMobile flag ONLY (not checked in this fixture).
    DriverFactory handles branching.
    
    Scope: function (new driver per test)
    Lifecycle:
    - Setup: Create driver, set correlation ID for logging
    - Teardown: Close driver, clean up resources
    
    Args:
        is_mobile: Session-scoped isMobile flag.
        event_loop: Event loop for async operations.
        request: pytest request object (for test name).
    
    Yields:
        IDriverProvider: Web (Playwright) or Mobile (Appium) driver wrapper.
    """
    # Set correlation ID for logging (test name + thread ID)
    test_name = request.node.name
    StructuredLogger.set_correlation_id(test_name)
    
    logger.info(f"Setting up driver for test: {test_name}")
    artifacts = getattr(request.config, "_run_artifacts", {})
    trace_path = None
    driver_instance = None
    
    # Create driver based on is_mobile flag (synchronous)
    try:
        if is_mobile:
            # Mobile: Appium (sync)
            driver_instance = DriverFactory.create_mobile_driver()
        else:
            # Web: Playwright (async)
            driver_instance = event_loop.run_until_complete(DriverFactory.create_driver(is_mobile))
            trace_dir = artifacts.get("traces", "reports/playwright-traces")
            os.makedirs(trace_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            safe_name = _sanitize_filename(test_name)
            trace_path = f"{trace_dir}/{safe_name}-{timestamp}.zip"

            # Capture Playwright native trace for each web test.
            if hasattr(driver_instance, "start_trace"):
                event_loop.run_until_complete(driver_instance.start_trace(trace_path))
        driver_instance = event_loop.run_until_complete(DriverFactory.create_driver(is_mobile))
        
        logger.info("Driver fixture initialized successfully")
        yield driver_instance
    
    except Exception as e:
        logger.error(f"Failed to initialize driver: {e}")
        raise
    
    finally:
        # Teardown: Close driver
        logger.info("Tearing down driver fixture")
        try:
            if (not is_mobile) and trace_path:
                logger.info(f"Playwright trace target: {trace_path}")

            if is_mobile:
                driver_instance.close()
            else:
                if driver_instance is not None:
                    event_loop.run_until_complete(driver_instance.close())
                    logger.info("Driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing driver: {e}")


# ===== PAGE FACTORY FIXTURE =====

@pytest.fixture
def page_factory(driver, is_mobile):
    """
    Provide PageObjectFactory to test.
    
    Factory returns page implementations based on isMobile flag.
    Tests call factory.get_xxx_page() to get interface implementations.
    
    Args:
        driver: Driver fixture.
        is_mobile: Session-scoped isMobile flag.
    
    Returns:
        PageObjectFactory: Factory for getting page implementations.
    """
    logger.info("Creating PageObjectFactory")
    return PageObjectFactory(driver, is_mobile)


# ===== TEST LIFECYCLE HOOKS =====

@pytest.fixture(autouse=True)
def log_test_lifecycle(request):
    """
    Log test start and end with correlation ID.
    
    Runs for every test automatically (autouse=True).
    
    Args:
        request: pytest request object.
    """
    test_name = request.node.name
    StructuredLogger.set_correlation_id(test_name)
    
    start_time = time.time()
    logger.info(f"{'='*70}")
    logger.info(f"TEST START: {test_name}")
    logger.info(f"{'='*70}")
    
    yield
    
    elapsed = time.time() - start_time
    logger.info(f"{'='*70}")
    logger.info(f"TEST END: {test_name} (duration: {elapsed:.2f}s)")
    logger.info(f"{'='*70}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Centralized failure hook — captures screenshot + diagnostics on test failure.
    
    Runs after each test call.
    On failure, captures:
    - Screenshot (if driver available)
    - Page source (Web) or Logcat (Mobile)
    - Diagnostic dump to logs/diagnostics/<correlationId>.txt
    
    Args:
        item: pytest test item.
        call: test call object (setup, call, teardown phases).
    """
    outcome = yield
    
    # Only capture diagnostics on failure in the test call phase
    if outcome.excinfo and call.when == "call":
        logger.error(f"TEST FAILED: {item.name}")
        
        # Try to capture driver for diagnostics
        driver = item.funcargs.get('driver')
        if driver:
            try:
                artifacts = getattr(item.config, "_run_artifacts", {})
                screenshots_dir = artifacts.get("screenshots", "reports/screenshots")

                # Capture screenshot
                screenshot_path = None
                if hasattr(driver, 'get_page'):
                    page = driver.get_page()
                    if hasattr(page, 'screenshot'):
                        # Playwright
                        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                        screenshot_path = f"{screenshots_dir}/{item.name}-{timestamp}.png"
                        page.screenshot(path=screenshot_path)
                        screenshot_path = f"reports/screenshots/{item.name}-{timestamp}.png"
                        event_loop = item.funcargs.get('event_loop')
                        if event_loop:
                            event_loop.run_until_complete(page.screenshot(path=screenshot_path))
                        logger.error(f"Screenshot captured: {screenshot_path}")
                    elif hasattr(page, 'save_screenshot'):
                        # Appium
                        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                        screenshot_path = f"{screenshots_dir}/{item.name}-{timestamp}.png"
                        page.save_screenshot(screenshot_path)
                        logger.error(f"Screenshot captured: {screenshot_path}")
            except Exception as e:
                logger.error(f"Failed to capture diagnostics: {e}")


# ===== CLI OPTIONS =====

def pytest_addoption(parser):
    """
    Add custom CLI options.
    
    Allows user to run tests in Mobile mode:
        pytest tests/ --isMobile
    
    Without flag, defaults to Web mode.
    """
    parser.addoption(
        "--isMobile",
        action="store_true",
        default=False,
        help="Run tests in Mobile mode (Appium). Default: Web mode (Playwright)"
    )
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Playwright browser: chromium|chrome|firefox|webkit|edge"
    )
    parser.addoption(
        "--browser-channel",
        action="store",
        default=None,
        help="Playwright browser channel, e.g. chrome or msedge"
    )
    parser.addoption(
        "--device",
        action="store",
        default=None,
        help="Playwright device descriptor, e.g. 'iPhone 13' or 'Pixel 5'"
    )
    parser.addoption(
        "--viewport",
        action="store",
        default=None,
        help="Viewport size for desktop mode in WIDTHxHEIGHT format, e.g. 1920x1080"
    )
    parser.addoption(
        "--headless",
        action="store_const",
        const=True,
        dest="headless_mode",
        default=None,
        help="Force headless browser mode"
    )
    parser.addoption(
        "--headed",
        action="store_const",
        const=False,
        dest="headless_mode",
        default=None,
        help="Force headed browser mode"
    )


# ===== PYTEST CONFIGURATION =====

def pytest_configure(config):
    """
    Configure pytest at startup.
    
    If --isMobile CLI arg provided, set IS_MOBILE env var for ConfigLoader.
    
    Args:
        config: pytest Config object.
    """
    artifacts = _build_run_artifact_paths()
    config._run_artifacts = artifacts
    config._run_started_at = time.time()

    import os
    os.environ["SCREENSHOTS_DIR"] = artifacts["screenshots"]

    # Force per-run report files across supported plugins.
    config.option.htmlpath = artifacts["html"]
    config.option.xmlpath = artifacts["junit"]

    if hasattr(config.option, "json_report"):
        config.option.json_report = True
    if hasattr(config.option, "json_report_file"):
        config.option.json_report_file = artifacts["json"]
    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = artifacts["allure"]

    logger.info(
        "Run artifacts: html=%s junit=%s json=%s allure=%s",
        artifacts["html"],
        artifacts["junit"],
        artifacts["json"],
        artifacts["allure"],
    )

    if config.getoption("--isMobile", default=False):
        os.environ['IS_MOBILE'] = 'true'
        logger.info("CLI arg --isMobile detected; setting IS_MOBILE=true")

    browser = config.getoption("--browser", default=None)
    if browser:
        normalized_browser = browser.strip().lower()
        os.environ['BROWSER'] = normalized_browser
        if normalized_browser == 'chrome' and not os.getenv('BROWSER_CHANNEL'):
            os.environ['BROWSER_CHANNEL'] = 'chrome'
        if normalized_browser == 'edge' and not os.getenv('BROWSER_CHANNEL'):
            os.environ['BROWSER_CHANNEL'] = 'msedge'
        logger.info("CLI arg --browser detected; setting BROWSER=%s", normalized_browser)

    browser_channel = config.getoption("--browser-channel", default=None)
    if browser_channel:
        os.environ['BROWSER_CHANNEL'] = browser_channel.strip()
        logger.info("CLI arg --browser-channel detected; setting BROWSER_CHANNEL=%s", os.environ['BROWSER_CHANNEL'])

    device_name = config.getoption("--device", default=None)
    if device_name:
        os.environ['PLAYWRIGHT_DEVICE'] = device_name.strip()
        logger.info("CLI arg --device detected; setting PLAYWRIGHT_DEVICE=%s", os.environ['PLAYWRIGHT_DEVICE'])

    viewport = config.getoption("--viewport", default=None)
    if viewport:
        normalized = viewport.lower().replace(" ", "")
        if "x" not in normalized:
            raise pytest.UsageError("Invalid --viewport value. Use WIDTHxHEIGHT, e.g. 1366x768")
        width_text, height_text = normalized.split("x", 1)
        if not width_text.isdigit() or not height_text.isdigit():
            raise pytest.UsageError("Invalid --viewport value. Width and height must be numeric.")
        os.environ['VIEWPORT_WIDTH'] = width_text
        os.environ['VIEWPORT_HEIGHT'] = height_text
        # Device profile and custom viewport are mutually exclusive.
        os.environ.pop('PLAYWRIGHT_DEVICE', None)
        logger.info(
            "CLI arg --viewport detected; setting VIEWPORT_WIDTH=%s VIEWPORT_HEIGHT=%s",
            width_text,
            height_text,
        )

    headless_mode = config.getoption("headless_mode", default=None)
    if headless_mode is not None:
        os.environ['HEADLESS'] = 'true' if headless_mode else 'false'
        logger.info("CLI arg --headless/--headed detected; setting HEADLESS=%s", os.environ['HEADLESS'])


def pytest_html_report_title(report):
    """Set a friendlier title in the pytest-html report."""
    report.title = "Gajab Automation - Execution Report"


def pytest_sessionfinish(session, exitstatus):
    """Create a run-level dashboard summarizing key report artifacts."""
    artifacts = getattr(session.config, "_run_artifacts", None)
    if not artifacts:
        return

    terminal_reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    stats = terminal_reporter.stats if terminal_reporter else {}

    counts = {
        "collected": session.testscollected,
        "passed": len(stats.get("passed", [])),
        "failed": len(stats.get("failed", [])) + len(stats.get("error", [])),
        "skipped": len(stats.get("skipped", [])) + len(stats.get("xfailed", [])) + len(stats.get("xpassed", [])),
    }

    started = getattr(session.config, "_run_started_at", time.time())
    duration_sec = max(0.0, time.time() - started)

    _write_run_dashboard(artifacts, counts, duration_sec, exitstatus)
    logger.info("Run dashboard created: %s", artifacts["dashboard"])
