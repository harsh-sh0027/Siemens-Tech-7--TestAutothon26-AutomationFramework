"""Explicit wait utilities — NO hardcoded sleeps.

All waits use config-driven timeouts and poll intervals.
Condition-based waits that translate driver exceptions to custom exceptions.
"""

import time
from typing import Callable, Optional

from src.utils.config import ConfigLoader
from src.utils.logger import StructuredLogger
from src.exceptions import ElementNotFoundException, PageLoadTimeoutException

logger = StructuredLogger.get_logger(__name__)


class WaitUtilities:
    """
    Explicit waits for Web (Playwright) and Mobile (Appium).
    
    - NO hardcoded sleeps anywhere
    - All timeouts and poll intervals from config
    - Translates raw driver exceptions to custom exceptions
    - Includes element locator and action in error messages
    """
    
    @staticmethod
    def wait_for_condition(
        condition: Callable[[], bool],
        timeout: Optional[int] = None,
        poll_interval: Optional[float] = None,
        error_msg: str = "Condition not met"
    ) -> bool:
        """
        Wait for a boolean condition to return True.
        
        Args:
            condition: Callable that returns bool (True = success).
            timeout: Timeout in seconds (from config if None).
            poll_interval: Poll interval in seconds (from config if None).
            error_msg: Error message if timeout occurs.
            
        Returns:
            bool: True if condition met within timeout.
            
        Raises:
            TimeoutError: If condition not met within timeout.
        """
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        poll_interval = poll_interval or ConfigLoader.poll_interval()
        
        start_time = time.time()
        last_exception = None
        
        while time.time() - start_time < timeout:
            try:
                if condition():
                    elapsed = time.time() - start_time
                    logger.debug(f"Condition met after {elapsed:.2f}s")
                    return True
            except Exception as e:
                last_exception = e
                logger.debug(f"Condition check failed: {type(e).__name__}: {e}")
            
            time.sleep(poll_interval)
        
        elapsed = time.time() - start_time
        logger.error(f"Timeout after {elapsed:.2f}s: {error_msg}")
        
        if last_exception:
            raise TimeoutError(f"{error_msg} (Last exception: {type(last_exception).__name__}: {last_exception})") from last_exception
        raise TimeoutError(error_msg)
    
    @staticmethod
    async def wait_for_visible(page, selector: str, timeout: Optional[int] = None):
        """
        Wait for element to be visible.
        
        Args:
            page: Playwright page or Appium driver.
            selector: Locator selector (CSS for Web, XPath for Mobile).
            timeout: Timeout in seconds (from config if None).
            
        Returns:
            Element/Locator object.
            
        Raises:
            ElementNotFoundException: If element not visible within timeout.
        """
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        logger.debug(f"Waiting for visible element: {selector} (timeout: {timeout}s)")
        
        try:
            # Playwright syntax (has .locator method)
            if hasattr(page, 'locator'):
                element = page.locator(selector)
                await element.wait_for(timeout=timeout * 1000, state='visible')
                logger.debug(f"Element visible: {selector}")
                return element
            
            # Appium syntax (has .find_element method)
            elif hasattr(page, 'find_element'):
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.common.by import By
                
                wait = WebDriverWait(page, timeout)
                element = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
                logger.debug(f"Element visible: {selector}")
                return element
        except Exception as e:
            logger.error(f"Failed to find visible element: {selector} - {type(e).__name__}: {e}")
            raise ElementNotFoundException(
                f"Element not found or not visible: {selector} (timeout: {timeout}s)"
            ) from e
    
    @staticmethod
    async def wait_for_clickable(page, selector: str, timeout: Optional[int] = None):
        """
        Wait for element to be clickable.
        
        Args:
            page: Playwright page or Appium driver.
            selector: Locator selector.
            timeout: Timeout in seconds (from config if None).
            
        Returns:
            Element/Locator object.
            
        Raises:
            ElementNotFoundException: If element not clickable within timeout.
        """
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        logger.debug(f"Waiting for clickable element: {selector}")
        
        # First, wait for visibility
        element = await WaitUtilities.wait_for_visible(page, selector, timeout)
        
        try:
            if hasattr(page, 'locator'):
                # Playwright: wait for enabled state
                await page.locator(selector).wait_for(timeout=timeout * 1000, state='attached')
            elif hasattr(element, 'is_enabled'):
                # Appium: check enabled
                if not element.is_enabled():
                    raise ElementNotFoundException(f"Element not enabled: {selector}")
        except Exception as e:
            logger.error(f"Element not clickable: {selector} - {e}")
            raise ElementNotFoundException(
                f"Element not clickable: {selector}"
            ) from e
        
        logger.debug(f"Element clickable: {selector}")
        return element
    
    @staticmethod
    def wait_for_invisible(page, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for element to be invisible or hidden.
        
        Args:
            page: Playwright page or Appium driver.
            selector: Locator selector.
            timeout: Timeout in seconds (from config if None).
            
        Returns:
            bool: True if element became invisible.
            
        Raises:
            PageLoadTimeoutException: If element still visible after timeout.
        """
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        logger.debug(f"Waiting for invisible element: {selector}")
        
        try:
            if hasattr(page, 'locator'):
                # Playwright
                page.locator(selector).wait_for(timeout=timeout * 1000, state='hidden')
                logger.debug(f"Element invisible: {selector}")
                return True
            elif hasattr(page, 'find_element'):
                # Appium
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.common.by import By
                
                wait = WebDriverWait(page, timeout)
                wait.until(EC.invisibility_of_element_located((By.XPATH, selector)))
                logger.debug(f"Element invisible: {selector}")
                return True
        except Exception as e:
            logger.error(f"Element still visible: {selector} - {e}")
            raise PageLoadTimeoutException(
                f"Element did not become invisible: {selector} (timeout: {timeout}s)"
            ) from e
    
    @staticmethod
    def wait_for_text_present(
        page,
        selector: str,
        text: str,
        timeout: Optional[int] = None,
        partial: bool = False
    ) -> bool:
        """
        Wait for element to contain text.
        
        Args:
            page: Playwright page or Appium driver.
            selector: Locator selector.
            text: Text to find (exact or partial).
            timeout: Timeout in seconds (from config if None).
            partial: If True, matches partial text; if False, exact match.
            
        Returns:
            bool: True if text found.
            
        Raises:
            ElementNotFoundException: If text not found within timeout.
        """
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        logger.debug(f"Waiting for text '{text}' in element: {selector} (partial={partial})")
        
        def check_text():
            try:
                if hasattr(page, 'locator'):
                    # Playwright
                    element = page.locator(selector)
                    current_text = element.text_content()
                else:
                    # Appium
                    element = WaitUtilities.wait_for_visible(page, selector, 1)
                    current_text = element.text
                
                if not current_text:
                    return False
                
                if partial:
                    return text in current_text
                else:
                    return text == current_text.strip()
            except Exception as e:
                logger.debug(f"Error checking text: {e}")
                return False
        
        try:
            return WaitUtilities.wait_for_condition(
                check_text,
                timeout=timeout,
                error_msg=f"Text '{text}' not found in {selector}"
            )
        except TimeoutError as e:
            raise ElementNotFoundException(f"Text not found: {text} in {selector}") from e
    
    @staticmethod
    def wait_for_loading_complete(
        page,
        loading_selector: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for loading indicator to disappear.
        
        Used for SPA (Single Page Application) pages where loading spinners appear/disappear.
        
        Args:
            page: Playwright page or Appium driver.
            loading_selector: Selector for loading indicator.
            timeout: Timeout in seconds (from config if None).
            
        Returns:
            bool: True if loading completed.
            
        Raises:
            PageLoadTimeoutException: If loading still present after timeout.
        """
        logger.debug(f"Waiting for loading to complete (indicator: {loading_selector})")
        
        try:
            return WaitUtilities.wait_for_invisible(page, loading_selector, timeout)
        except PageLoadTimeoutException:
            raise
