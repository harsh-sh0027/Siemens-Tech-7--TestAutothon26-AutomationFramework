"""Base screen for all Mobile screens (Appium-backed).

Common behavior for all Mobile page objects.
"""

import os
from datetime import datetime
from selenium.webdriver.common.by import By

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
        capabilities = getattr(driver, 'capabilities', {}) or {}
        self.uses_browser = bool(capabilities.get('browserName'))
        logger.info(f"Initializing {self.__class__.__name__}")
    
    def get_page(self):
        """Return Appium driver."""
        return self.driver
    
    async def navigate_to(self, url: str = None):
        """
        Launch app or mobile website.
        
        Native app sessions are already launched by Appium. Browser sessions
        navigate to the provided URL inside Android Chrome.
        
        Args:
            url: URL for mobile web runs.
        """
        if self.uses_browser:
            target_url = url or ConfigLoader.base_url()
            logger.info(f"Opening mobile website: {target_url}")
            self.driver.get(target_url)
            await WaitUtilities.wait_for_visible(self.driver, 'css=body')
            return

        logger.info(f"Starting app: {ConfigLoader.app_package()}")
    
    async def find_element(self, selector: str):
        """
        Find element by resource ID or XPath.
        
        Args:
            selector: Resource ID or XPath locator.
            
        Returns:
            Appium WebElement.
        """
        logger.debug(f"Finding element: {selector}")
        return await WaitUtilities.wait_for_visible(self.driver, selector)

    async def _handle_android_permission_popup(self) -> bool:
        """Dismiss Android permission prompts by choosing Never allow/Don't allow when present."""
        if not hasattr(self.driver, 'switch_to'):
            return False

        clicked = False
        original_context = None
        contexts = ['NATIVE_APP']

        try:
            if hasattr(self.driver, 'current_context'):
                original_context = self.driver.current_context
            if hasattr(self.driver, 'contexts'):
                for context in self.driver.contexts:
                    if context not in contexts:
                        contexts.append(context)
        except Exception:
            pass

        locators = [
            (By.ID, 'com.android.permissioncontroller:id/permission_deny_and_dont_ask_again_button'),
            (By.ID, 'com.android.permissioncontroller:id/permission_deny_button'),
            (By.ID, 'com.android.chrome:id/negative_button'),
            (By.XPATH, "//*[contains(@text, 'Never allow') or contains(@text, 'NEVER ALLOW')]"),
            (By.XPATH, "//*[contains(@text, \"Don't allow\") or contains(@text, 'DON\'T ALLOW')]"),
        ]

        for context in contexts:
            try:
                self.driver.switch_to.context(context)
            except Exception:
                continue

            for by, value in locators:
                try:
                    elements = self.driver.find_elements(by, value)
                    if not elements:
                        continue
                    elements[0].click()
                    logger.info("Permission popup detected; selected Never allow/Don't allow")
                    clicked = True
                    break
                except Exception:
                    continue

            if clicked:
                break

        if original_context:
            try:
                self.driver.switch_to.context(original_context)
            except Exception:
                pass

        return clicked

    async def _dismiss_browser_coachmark_overlay(self) -> bool:
        """Dismiss in-page promotional coachmark overlays that block actions on mobile web."""
        if not self.uses_browser:
            return False

        try:
            removed = self.driver.execute_script(
                "const markers=['Start Your First Bargain Today', 'people have signed up last 24 hours'];"
                "let changed=false;"
                "for (const marker of markers) {"
                "  const el=[...document.querySelectorAll('body *')].find(n => (n.innerText||'').includes(marker));"
                "  if (!el) continue;"
                "  let host=el;"
                "  while (host && host !== document.body) {"
                "    const style=getComputedStyle(host);"
                "    if (style.position==='fixed' || style.position==='sticky' || parseInt(style.zIndex || '0', 10) > 100) {"
                "      host.style.display='none';"
                "      changed=true;"
                "      break;"
                "    }"
                "    host=host.parentElement;"
                "  }"
                "}"
                "return changed;"
            )
            if removed:
                logger.info("Dismissed blocking in-page coachmark overlay")
            return bool(removed)
        except Exception:
            return False

    async def _handle_browser_permission_popup(self) -> bool:
        """Dismiss browser-level permission sheets by selecting Never allow/Don't allow when visible."""
        if not self.uses_browser:
            return False

        try:
            clicked = self.driver.execute_script(
                "const labels = ['Never allow', 'NEVER ALLOW', \"Don't allow\", \"DON'T ALLOW\"];"
                "const candidates = [...document.querySelectorAll('button, [role=button], div, span')];"
                "for (const node of candidates) {"
                "  const text = (node.innerText || node.textContent || '').trim();"
                "  if (!labels.some(l => text.includes(l))) continue;"
                "  node.click();"
                "  return true;"
                "}"
                "return false;"
            )
            if clicked:
                logger.info("Browser permission popup detected; selected Never allow/Don't allow")
            return bool(clicked)
        except Exception:
            return False

    async def _handle_optional_popups(self):
        """Run popup handlers opportunistically before/after interactions."""
        await self._handle_android_permission_popup()
        await self._handle_browser_permission_popup()
        await self._dismiss_browser_coachmark_overlay()
    
    async def safe_click(self, selector: str):
        """
        Click element safely (wait for clickable + click).
        
        Args:
            selector: Resource ID or XPath locator.
            
        Raises:
            ElementNotFoundException: If element not clickable.
        """
        logger.info(f"Clicking element: {selector}")
        await self._handle_optional_popups()

        last_error = None
        for attempt in range(2):
            try:
                element = await WaitUtilities.wait_for_clickable(self.driver, selector)
                try:
                    element.click()
                except Exception:
                    if not self.uses_browser:
                        raise

                    logger.debug(f"Native click failed for browser session, retrying via DOM click: {selector}")
                    self.driver.execute_script("arguments[0].click();", element)
                logger.debug(f"Clicked: {selector}")
                return
            except Exception as e:
                last_error = e
                if attempt == 0:
                    await self._handle_optional_popups()
                    continue

        logger.error(f"Click failed: {selector} - {last_error}")
        await self.take_screenshot("click_failed")
        raise last_error
    
    async def safe_type(self, selector: str, text: str):
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
            element = await WaitUtilities.wait_for_visible(self.driver, selector)
            element.clear()
            element.send_keys(text)
            if self.uses_browser:
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
                    "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                    element,
                )
            logger.debug(f"Typed into: {selector}")
        except Exception as e:
            logger.error(f"Type failed: {selector} - {e}")
            await self.take_screenshot("type_failed")
            raise
    
    async def safe_get_text(self, selector: str) -> str:
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
            element = await WaitUtilities.wait_for_visible(self.driver, selector)
            text = element.text
            text_preview = text[:50] + "..." if len(text) > 50 else text
            logger.debug(f"Text from {selector}: {text_preview}")
            return text or ""
        except Exception as e:
            logger.error(f"Get text failed: {selector} - {e}")
            raise
    
    async def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500):
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
    
    async def scroll_to_element(self, selector: str):
        """
        Scroll to element by using swipe gestures.
        
        Simple scroll down; for more complex scrolling, use swipe() directly.
        
        Args:
            selector: Resource ID or XPath locator.
        """
        logger.debug(f"Scrolling to element: {selector}")
        try:
            if self.uses_browser:
                element = await self.find_element(selector)
                self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
                logger.debug(f"Scrolled to: {selector}")
                return

            # Try to find element; if not found, scroll down
            size = self.driver.get_window_size()
            height = size['height']
            width = size['width']
            
            # Scroll down
            await self.swipe(width // 2, height // 2, width // 2, height // 4)
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
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def get_page_source(self) -> str:
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
    
    async def get_logcat(self, lines: int = 100) -> str:
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
