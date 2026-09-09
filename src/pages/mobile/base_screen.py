"""Base screen for all Mobile screens (Appium-backed).

Common behavior for all Mobile page objects.
"""

import os
from datetime import datetime

from src.utils.logger import StructuredLogger
from src.utils.waits import WaitUtilities
from src.utils.config import ConfigLoader
from src.pages.interfaces.base_page import IBasePage

logger = StructuredLogger.get_logger(__name__)


class BaseScreen(IBasePage):
    """
    Base screen for all Mobile screens (Appium-backed).
    
    Provides common behavior:
    - Element finding with explicit waits
    - Safe click, type, get_text (with waits)
    - Screenshot capture
    - Swipe gestures
    - App launch/reset
    
    All locators and screen-specific behavior in subclasses.
    """
    
    def __init__(self, driver, is_mobile: bool = True):
        """
        Initialize base screen.
        
        Args:
            driver: Appium WebDriver instance.
            is_mobile: Flag indicating mobile mode (True for Mobile).
        """
        self.driver = driver
        self.is_mobile = is_mobile
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def get_page(self):
        """Return Appium driver."""
        return self.driver
    
    def navigate_to(self, url: str = None):
        """
        Launch app (Mobile).
        
        App is already launched via fixture; this is mainly for compatibility.
        
        Args:
            url: Unused for Mobile (kept for interface compatibility).
        """
        logger.info(f"Starting app: {ConfigLoader.app_package()}")
        # App already launched via fixture; this is no-op
    
    def find_element(self, selector: str):
        """
        Find element by resource ID or XPath.
        
        Args:
            selector: Resource ID or XPath locator.
            
        Returns:
            Appium WebElement.
        """
        logger.debug(f"Finding element: {selector}")
        return WaitUtilities.wait_for_visible(self.driver, selector)
    
    def safe_click(self, selector: str):
        """
        Click element safely (wait for clickable + click).
        
        Args:
            selector: Resource ID or XPath locator.
            
        Raises:
            ElementNotFoundException: If element not clickable.
        """
        logger.info(f"Clicking element: {selector}")
        try:
            element = WaitUtilities.wait_for_clickable(self.driver, selector)
            element.click()
            logger.debug(f"Clicked: {selector}")
        except Exception as e:
            logger.error(f"Click failed: {selector} - {e}")
            self.take_screenshot("click_failed")
            raise
    
    def safe_type(self, selector: str, text: str):
        """
        Type text into element safely (wait + send keys).
        
        Args:
            selector: Resource ID or XPath locator.
            text: Text to type.
            
        Raises:
            ElementNotFoundException: If element not found.
        """
        logger.info(f"Typing into {selector}: [REDACTED]" if len(text) > 0 else f"Typing into {selector}: (empty)")
        try:
            element = WaitUtilities.wait_for_visible(self.driver, selector)
            element.clear()
            element.send_keys(text)
            logger.debug(f"Typed into: {selector}")
        except Exception as e:
            logger.error(f"Type failed: {selector} - {e}")
            self.take_screenshot("type_failed")
            raise
    
    def safe_get_text(self, selector: str) -> str:
        """
        Get text from element safely (wait + get text).
        
        Args:
            selector: Resource ID or XPath locator.
            
        Returns:
            str: Text content of element.
            
        Raises:
            ElementNotFoundException: If element not found.
        """
        logger.debug(f"Getting text from: {selector}")
        try:
            element = WaitUtilities.wait_for_visible(self.driver, selector)
            text = element.text
            text_preview = text[:50] + "..." if len(text) > 50 else text
            logger.debug(f"Text from {selector}: {text_preview}")
            return text or ""
        except Exception as e:
            logger.error(f"Get text failed: {selector} - {e}")
            raise
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500):
        """
        Perform swipe gesture on screen.
        
        Args:
            start_x: Start X coordinate.
            start_y: Start Y coordinate.
            end_x: End X coordinate.
            end_y: End Y coordinate.
            duration: Swipe duration in milliseconds (default: 500).
        """
        logger.info(f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            logger.debug("Swipe completed")
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            raise
    
    def scroll_to_element(self, selector: str):
        """
        Scroll to element by using swipe gestures.
        
        Simple scroll down; for more complex scrolling, use swipe() directly.
        
        Args:
            selector: Resource ID or XPath locator.
        """
        logger.debug(f"Scrolling to element: {selector}")
        try:
            # Try to find element; if not found, scroll down
            size = self.driver.get_window_size()
            height = size['height']
            width = size['width']
            
            # Scroll down
            self.swipe(width // 2, height // 2, width // 2, height // 4)
            logger.debug(f"Scrolled to: {selector}")
        except Exception as e:
            logger.error(f"Scroll failed: {selector} - {e}")
            raise
    
    def take_screenshot(self, name: str) -> str:
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
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    def get_page_source(self) -> str:
        """
        Get page XML source (Android app hierarchy).
        
        Useful for diagnostics on failure.
        
        Returns:
            str: Full page XML hierarchy.
        """
        try:
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""
    
    def get_logcat(self, lines: int = 100) -> str:
        """
        Get device logcat output.
        
        Useful for debugging app crashes and errors.
        
        Args:
            lines: Number of recent log lines to retrieve (default: 100).
            
        Returns:
            str: Logcat output.
        """
        try:
            logs = self.driver.get_log('logcat')
            return "\n".join([str(log) for log in logs[-lines:]])
        except Exception as e:
            logger.error(f"Failed to get logcat: {e}")
            return ""
