"""Base page for all Web pages (Playwright-backed).

Common behavior for all Web page objects.
"""

import os
import asyncio
from datetime import datetime

from src.utils.logger import StructuredLogger
from src.utils.waits import WaitUtilities
from src.utils.config import ConfigLoader
from src.pages.interfaces.base_page import IBasePage

logger = StructuredLogger.get_logger(__name__)


def _run_async(coro):
    """Helper to run async coroutine from sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create one
        return asyncio.run(coro)
    else:
        # Running loop exists - create a task and wait
        import concurrent.futures
        import threading
        
        future = concurrent.futures.Future()
        
        def set_result():
            try:
                result = asyncio.run(coro)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
        
        threading.Thread(target=set_result, daemon=True).start()
        return future.result(timeout=30)


"""Base page for all Web pages (Playwright-backed).

Common behavior for all Web page objects.
"""

import os
import asyncio
from datetime import datetime

from src.utils.logger import StructuredLogger
from src.utils.waits import WaitUtilities
from src.utils.config import ConfigLoader
from src.pages.interfaces.base_page import IBasePage

logger = StructuredLogger.get_logger(__name__)


class BasePage(IBasePage):
    """
    Base page for all Web pages (Playwright-backed).
    
    Provides common behavior:
    - Element finding with explicit waits
    - Safe click, type, get_text (with waits)
    - Screenshot capture
    - Navigation
    
    All locators and page-specific behavior in subclasses.
    """
    
    def __init__(self, page, is_mobile: bool = False):
        """
        Initialize base page.
        
        Args:
            page: Playwright Page instance.
            is_mobile: Flag indicating mobile mode (False for Web).
        """
        self.page = page
        self.is_mobile = is_mobile
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def get_page(self):
        """Return Playwright page."""
        return self.page
    
    async def navigate_to(self, url: str):
        """
        Navigate to URL.
        
        Args:
            url: Full URL to navigate to.
        """
        logger.info(f"Navigating to: {url}")
        try:
            await self.page.goto(url, wait_until='networkidle')
            # Wait for body to ensure page is loaded
            await WaitUtilities.wait_for_visible(self.page, "body")
            logger.info(f"Page loaded: {url}")
        except Exception as e:
            logger.error(f"Navigation failed: {url} - {e}")
            await self.take_screenshot("navigation_failed")
            raise
    
    async def find_element(self, selector: str):
        """
        Find element by selector (with wait for visibility).
        
        Args:
            selector: CSS selector or Playwright locator.
            
        Returns:
            Playwright Locator.
        """
        logger.debug(f"Finding element: {selector}")
        return await WaitUtilities.wait_for_visible(self.page, selector)
    
    async def safe_click(self, selector: str):
        """
        Click element safely (wait for clickable + click).
        
        Args:
            selector: CSS selector or Playwright locator.
            
        Raises:
            ElementNotFoundException: If element not clickable.
        """
        logger.info(f"Clicking element: {selector}")
        try:
            element = await WaitUtilities.wait_for_clickable(self.page, selector)
            await element.click()
            logger.debug(f"Clicked: {selector}")
        except Exception as e:
            logger.error(f"Click failed: {selector} - {e}")
            await self.take_screenshot("click_failed")
            raise
    
    async def safe_type(self, selector: str, text: str):
        """
        Type text into element safely (wait + fill).
        
        Args:
            selector: CSS selector or Playwright locator.
            text: Text to type.
            
        Raises:
            ElementNotFoundException: If element not found.
        """
        logger.info(f"Typing into {selector}: [REDACTED]" if len(text) > 0 else f"Typing into {selector}: (empty)")
        try:
            element = await WaitUtilities.wait_for_visible(self.page, selector)
            await element.fill(text)
            logger.debug(f"Typed into: {selector}")
        except Exception as e:
            logger.error(f"Type failed: {selector} - {e}")
            await self.take_screenshot("type_failed")
            raise
    
    async def safe_get_text(self, selector: str) -> str:
        """
        Get text from element safely (wait + get text).
        
        Args:
            selector: CSS selector or Playwright locator.
            
        Returns:
            str: Text content of element.
            
        Raises:
            ElementNotFoundException: If element not found.
        """
        logger.debug(f"Getting text from: {selector}")
        try:
            element = await WaitUtilities.wait_for_visible(self.page, selector)
            text = await element.text_content()
            text_preview = text[:50] + "..." if len(text) > 50 else text
            logger.debug(f"Text from {selector}: {text_preview}")
            return text or ""
        except Exception as e:
            logger.error(f"Get text failed: {selector} - {e}")
            raise
    
    async def scroll_to_element(self, selector: str):
        """
        Scroll element into view.
        
        Args:
            selector: CSS selector or Playwright locator.
        """
        logger.debug(f"Scrolling to element: {selector}")
        try:
            element = await self.find_element(selector)
            await element.scroll_into_view_if_needed()
            logger.debug(f"Scrolled to: {selector}")
        except Exception as e:
            logger.error(f"Scroll failed: {selector} - {e}")
            raise
    
    async def take_screenshot(self, name: str) -> str:
        """
        Capture screenshot.
        
        Args:
            name: Screenshot name (without extension).
            
        Returns:
            str: Path to screenshot file.
        """
        try:
            os.makedirs(ConfigLoader.screenshots_dir(), exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"{ConfigLoader.screenshots_dir()}/{name}-{timestamp}.png"
            await self.page.screenshot(path=filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def get_page_source(self) -> str:
        """
        Get page HTML source.
        
        Useful for diagnostics on failure.
        
        Returns:
            str: Full page HTML.
        """
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""
