"""Base page for all Web pages (Playwright-backed).

Common behavior for all Web page objects.
"""

import os
from datetime import datetime

from src.exceptions import ElementNotFoundException
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
            # Some SPAs keep network busy; start with lighter readiness signals.
            try:
                await self.page.goto(url, wait_until='domcontentloaded')
            except Exception:
                await self.page.goto(url, wait_until='load')

            # Wait for body and attempt network idle as a best-effort only.
            await WaitUtilities.wait_for_visible(self.page, "body")
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                logger.debug("networkidle not reached; proceeding with visible DOM")
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

    async def find_first_visible(self, selectors, timeout=None):
        """Return the first visible element from a selector list."""
        timeout = timeout or ConfigLoader.explicit_wait_timeout()
        if isinstance(selectors, str):
            selectors = [selectors]

        last_error = None
        for selector in selectors:
            try:
                element = await WaitUtilities.wait_for_visible(self.page, selector, timeout)
                return selector, element
            except Exception as exc:
                last_error = exc
                logger.debug(f"Selector not matched yet: {selector} ({exc})")

        raise ElementNotFoundException(
            f"None of the selectors became visible: {selectors}"
        ) from last_error
    
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

    async def safe_click_any(self, selectors, timeout=None):
        """Click the first visible selector from a list."""
        selector, element = await self.find_first_visible(selectors, timeout)
        logger.info(f"Clicking first-matched selector: {selector}")
        try:
            await element.click(timeout=3000)
        except Exception as first_error:
            logger.warning(f"Standard click failed for {selector}: {first_error}")
            await self.dismiss_common_popups()
            await element.click(force=True, timeout=3000)
        return selector
    
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

    async def safe_type_any(self, selectors, text: str, timeout=None):
        """Type into the first visible selector from a list."""
        selector, element = await self.find_first_visible(selectors, timeout)
        logger.info(f"Typing into first-matched selector: {selector}")
        await element.fill(text)
        return selector
    
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

    async def safe_get_text_any(self, selectors, timeout=None) -> str:
        """Read text from the first visible selector from a list."""
        selector, element = await self.find_first_visible(selectors, timeout)
        text = await element.text_content()
        logger.debug(f"Text read from selector: {selector}")
        return text or ""
    
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

    async def dismiss_common_popups(self):
        """Dismiss common overlays/popups if present.

        Best-effort helper: intentionally ignores misses and continues.
        """
        # Neutralize known full-screen overlays that block pointer events.
        try:
            await self.page.evaluate(
                """
                () => {
                  const selectors = [
                    '#location-fullscreen-click-blocker',
                    '#home-bargain-guide-portal-overlay',
                    '#category-list-backdrop-overlay'
                  ];
                  for (const selector of selectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                      el.style.display = 'none';
                      el.style.visibility = 'hidden';
                      el.style.pointerEvents = 'none';
                    }
                  }
                }
                """
            )
        except Exception:
            pass

        popup_selectors = [
            "button[aria-label='Close']",
            "button:has-text('Close')",
            "button:has-text('Not now')",
            "button:has-text('Maybe later')",
            "button:has-text('Skip')",
            "button:has-text('No Thanks')",
            "[role='dialog'] button:has-text('X')",
            "[role='dialog'] button.close",
            "div[role='dialog'] button svg",
            "button:has-text('Got it')",
        ]

        # Special-case location gating modal observed on stg.gajab.com.
        try:
            location_modal = self.page.locator("section#location-desktop-dropdown").first
            if await location_modal.is_visible(timeout=700):
                pincode = os.getenv("TEST_PINCODE", "560037")

                pincode_inputs = [
                    "section#location-desktop-dropdown input[placeholder*='Pincode']",
                    "section#location-desktop-dropdown input[placeholder*='City']",
                    "section#location-desktop-dropdown input[type='text']",
                ]
                for selector in pincode_inputs:
                    locator = self.page.locator(selector).first
                    try:
                        if await locator.is_visible(timeout=500):
                            await locator.fill(pincode)
                            break
                    except Exception:
                        pass

                for selector in [
                    "section#location-desktop-dropdown [role='option']:has-text('560037')",
                    "section#location-desktop-dropdown li:has-text('560037')",
                    "section#location-desktop-dropdown button:has-text('Continue')",
                    "section#location-desktop-dropdown button:has-text('Confirm')",
                    "section#location-desktop-dropdown button:has-text('Submit')",
                    "section#location-desktop-dropdown button[aria-label='Close']",
                ]:
                    try:
                        candidate = self.page.locator(selector).first
                        if await candidate.is_visible(timeout=500):
                            await candidate.click(timeout=1200)
                    except Exception:
                        pass

                if await location_modal.is_visible(timeout=500):
                    await self.page.evaluate(
                        """
                        () => {
                          const el = document.querySelector('section#location-desktop-dropdown');
                          if (el) {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                            el.style.pointerEvents = 'none';
                          }
                        }
                        """
                    )

                await self.page.evaluate(
                    """
                    () => {
                      const blocker = document.querySelector('#location-fullscreen-click-blocker');
                      if (blocker) {
                        blocker.style.display = 'none';
                        blocker.style.visibility = 'hidden';
                        blocker.style.pointerEvents = 'none';
                      }
                    }
                    """
                )
                logger.info("Processed location modal popup")
        except Exception:
            pass

        for selector in popup_selectors:
            try:
                locator = self.page.locator(selector).first
                if await locator.is_visible(timeout=700):
                    await locator.click(timeout=1200)
                    logger.info(f"Dismissed popup using selector: {selector}")
            except Exception:
                # Popups are optional; ignore and continue.
                pass
    
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
