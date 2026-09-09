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
from datetime import datetime

from src.utils.config import ConfigLoader
from src.utils.logger import StructuredLogger
from src.fixtures.driver_factory import DriverFactory
from src.fixtures.page_factory import PageObjectFactory

logger = StructuredLogger.get_logger(__name__)


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
    
    # Create driver based on is_mobile flag (synchronous)
    try:
        if is_mobile:
            # Mobile: Appium (sync)
            driver_instance = DriverFactory.create_mobile_driver()
        else:
            # Web: Playwright (async)
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
            if is_mobile:
                driver_instance.close()
            else:
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
                # Capture screenshot
                screenshot_path = None
                if hasattr(driver, 'get_page'):
                    page = driver.get_page()
                    if hasattr(page, 'screenshot'):
                        # Playwright
                        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                        screenshot_path = f"reports/screenshots/{item.name}-{timestamp}.png"
                        page.screenshot(path=screenshot_path)
                        logger.error(f"Screenshot captured: {screenshot_path}")
                    elif hasattr(page, 'save_screenshot'):
                        # Appium
                        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                        screenshot_path = f"reports/screenshots/{item.name}-{timestamp}.png"
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


# ===== PYTEST CONFIGURATION =====

def pytest_configure(config):
    """
    Configure pytest at startup.
    
    If --isMobile CLI arg provided, set IS_MOBILE env var for ConfigLoader.
    
    Args:
        config: pytest Config object.
    """
    if config.getoption("--isMobile", default=False):
        import os
        os.environ['IS_MOBILE'] = 'true'
        logger.info("CLI arg --isMobile detected; setting IS_MOBILE=true")
