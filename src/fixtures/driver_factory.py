"""Driver factory — creates Web (Playwright) or Mobile (Appium) driver based on isMobile flag.

ONLY component allowed to branch on isMobile (besides PageObjectFactory).
All tests and pages are platform-agnostic.
"""

import asyncio
from typing import Union, Optional
from abc import ABC, abstractmethod

from src.utils.config import ConfigLoader
from src.utils.logger import StructuredLogger
from src.exceptions import DriverInitException

logger = StructuredLogger.get_logger(__name__)


class IDriverProvider(ABC):
    """Abstract interface for driver (Web or Mobile)."""
    
    @abstractmethod
    def get_page(self):
        """Return page object (for Playwright) or driver (for Appium)."""
        raise NotImplementedError
    
    @abstractmethod
    def get_driver(self):
        """Return raw driver (for advanced operations if needed)."""
        raise NotImplementedError
    
    @abstractmethod
    async def close(self):
        """Close driver/browser session."""
        raise NotImplementedError


class PlaywrightDriver(IDriverProvider):
    """
    Web driver via Playwright.
    
    Wraps Playwright browser, context, and page for unified interface.
    """
    
    def __init__(self, browser, context, page):
        """
        Initialize Playwright driver.
        
        Args:
            browser: Playwright Browser instance.
            context: Playwright BrowserContext instance.
            page: Playwright Page instance.
        """
        self._browser = browser
        self._context = context
        self._page = page
        self._trace_path = None
        self._trace_started = False
        self.is_mobile = False  # Web platform
        logger.info(f"PlaywrightDriver initialized (page: {page.url})")

    async def start_trace(self, trace_path: str):
        """Start Playwright built-in tracing for this test session."""
        if self._trace_started:
            return
        await self._context.tracing.start(screenshots=True, snapshots=True, sources=True)
        self._trace_path = trace_path
        self._trace_started = True
        logger.info(f"Playwright trace started: {trace_path}")
    
    def get_page(self):
        """Return Playwright page."""
        return self._page
    
    def get_driver(self):
        """Return Playwright page (acts as both page and driver)."""
        return self._page
    
    async def close(self):
        """Close Playwright browser and context."""
        logger.info("Closing Playwright driver")
        try:
            if self._trace_started and self._trace_path:
                await self._context.tracing.stop(path=self._trace_path)
                logger.info(f"Playwright trace saved: {self._trace_path}")
            await self._context.close()
            await self._browser.close()
            logger.info("Playwright driver closed")
        except Exception as e:
            logger.error(f"Error closing Playwright driver: {e}")


class AppiumDriver(IDriverProvider):
    """
    Mobile driver via Appium.
    
    Wraps Appium client for Android automation via UiAutomator2.
    """
    
    def __init__(self, driver):
        """
        Initialize Appium driver.
        
        Args:
            driver: Appium WebDriver instance.
        """
        self._driver = driver
        self.is_mobile = True  # Mobile platform
        logger.info(f"AppiumDriver initialized (package: {ConfigLoader.app_package()})")
    
    def get_driver(self):
        """Return Appium driver."""
        return self._driver
    
    def get_page(self):
        """Return Appium driver (acts as both page and driver for mobile)."""
        return self._driver
    
    async def close(self):
        """Close Appium session."""
        logger.info("Closing Appium driver")
        try:
            self._driver.quit()
            logger.info("Appium driver closed")
        except Exception as e:
            logger.error(f"Error closing Appium driver: {e}")


class DriverFactory:
    """
    Factory to create Web (Playwright) or Mobile (Appium) driver.
    
    CRITICAL: This is ONE of TWO places allowed to branch on isMobile flag.
    The other is PageObjectFactory.
    
    - Tests never check isMobile
    - Pages never check isMobile
    - Only DriverFactory and PageObjectFactory check isMobile
    """
    
    @staticmethod
    async def create_web_driver() -> PlaywrightDriver:
        """
        Create Playwright browser and page for Web automation.
        
        Returns:
            PlaywrightDriver: Wrapped Playwright page.
            
        Raises:
            DriverInitException: If browser launch fails.
        """
        logger.info(
            "Creating Playwright driver (browser: %s, channel: %s, headless: %s, device: %s, viewport: %sx%s)",
            ConfigLoader.browser(),
            ConfigLoader.browser_channel() or "default",
            ConfigLoader.headless(),
            ConfigLoader.playwright_device() or "none",
            ConfigLoader.viewport_width(),
            ConfigLoader.viewport_height(),
        )
        
        try:
            from playwright.async_api import async_playwright
            
            async_pw = await async_playwright().start()
            
            # Launch browser based on config
            browser_type = ConfigLoader.browser().lower()
            launch_kwargs = {"headless": ConfigLoader.headless()}
            browser_channel = ConfigLoader.browser_channel()
            if browser_type == 'chrome' and not browser_channel:
                browser_channel = 'chrome'
            elif browser_type == 'edge' and not browser_channel:
                browser_channel = 'msedge'

            if browser_type in ('chromium', 'chrome', 'edge') and browser_channel:
                launch_kwargs["channel"] = browser_channel

            if browser_type == 'firefox':
                browser = await async_pw.firefox.launch(**launch_kwargs)
            elif browser_type == 'webkit':
                browser = await async_pw.webkit.launch(**launch_kwargs)
            else:  # chromium family (default)
                browser = await async_pw.chromium.launch(**launch_kwargs)
            
            # Create context and page with either device profile or custom viewport.
            device_name = ConfigLoader.playwright_device()
            if device_name:
                device_descriptor = async_pw.devices.get(device_name)
                if not device_descriptor:
                    raise DriverInitException(
                        f"Unknown Playwright device profile: {device_name}. "
                        f"Use a valid name from Playwright devices list."
                    )
                context = await browser.new_context(**device_descriptor)
            else:
                context = await browser.new_context(
                    viewport={
                        "width": ConfigLoader.viewport_width(),
                        "height": ConfigLoader.viewport_height(),
                    }
                )

            page = await context.new_page()
            
            # Set navigation timeout
            page.set_default_timeout(ConfigLoader.page_load_timeout() * 1000)
            
            logger.info(f"Playwright driver created successfully")
            return PlaywrightDriver(browser, context, page)
        
        except Exception as e:
            logger.error(f"Failed to create Playwright driver: {type(e).__name__}: {e}")
            raise DriverInitException(f"Playwright driver initialization failed: {e}") from e
    
    @staticmethod
    def create_mobile_driver() -> AppiumDriver:
        """
        Create Appium driver for Android automation.
        
        Uses UiAutomator2 strategy to interact with native Android apps.
        
        Returns:
            AppiumDriver: Wrapped Appium driver.
            
        Raises:
            DriverInitException: If Appium connection fails.
        """
        logger.info(f"Creating Appium driver (host: {ConfigLoader.appium_host()}:{ConfigLoader.appium_port()})")
        
        try:
            from appium import webdriver as appium_webdriver
            from appium.options.android import UiAutomator2Options
            
            options = UiAutomator2Options()
            options.app_package = ConfigLoader.app_package()
            options.app_activity = ConfigLoader.app_activity()
            options.auto_grant_permissions = True
            options.new_command_timeout = ConfigLoader.page_load_timeout()
            
            # Connect to Appium server
            driver = appium_webdriver.Remote(
                f"http://{ConfigLoader.appium_host()}:{ConfigLoader.appium_port()}",
                options=options
            )
            
            logger.info(f"Appium driver created successfully (package: {ConfigLoader.app_package()})")
            return AppiumDriver(driver)
        
        except Exception as e:
            logger.error(f"Failed to create Appium driver: {type(e).__name__}: {e}")
            raise DriverInitException(f"Appium driver initialization failed: {e}") from e
    
    @staticmethod
    async def create_driver(is_mobile: bool) -> IDriverProvider:
        """
        Create driver based on isMobile flag.
        
        ONLY method allowed to branch on isMobile in this class.
        Rest of code (tests, pages, utilities) is completely platform-agnostic.
        
        Args:
            is_mobile: True for Appium/Android, False for Playwright.
            
        Returns:
            IDriverProvider: Web (Playwright) or Mobile (Appium) driver wrapper.
            
        Raises:
            DriverInitException: If driver creation fails.
        """
        if is_mobile:
            logger.info("=" * 60)
            logger.info("MOBILE RUN (Appium/Android/UiAutomator2)")
            logger.info("=" * 60)
            return DriverFactory.create_mobile_driver()
        else:
            logger.info("=" * 60)
            logger.info("WEB RUN (Playwright)")
            logger.info("=" * 60)
            return await DriverFactory.create_web_driver()
