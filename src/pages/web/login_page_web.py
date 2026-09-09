"""Web login page implementation (Playwright)."""

from src.pages.web.base_page_web import BasePage
from src.pages.interfaces.login_page import ILoginPage
from src.utils.logger import StructuredLogger
from src.exceptions import ElementNotFoundException, AuthenticationException

logger = StructuredLogger.get_logger(__name__)


class WebLoginPage(BasePage, ILoginPage):
    """
    Login page for Web (Playwright).
    
    Implements ILoginPage interface using Playwright-based interactions.
    Locators and interaction details specific to Web platform.
    """
    
    # Locators (from locator-inventory.md or actual Gajab staging app)
    # These are example locators; adjust per actual app structure
    MOBILE_INPUT = "input[placeholder*='Mobile'], input[name='mobile'], #mobile-input"
    REQUEST_OTP_BTN = "button:has-text('Request OTP'), button[type='submit']:first-of-type"
    OTP_INPUT = "input[maxlength='6'], input[placeholder*='OTP'], #otp-input"
    OTP_SUBMIT_BTN = "button:has-text('Verify OTP'), button[type='submit']"
    PIN_INPUT = "input[type='password'], input[placeholder*='PIN'], #pin-input"
    PIN_SUBMIT_BTN = "button:has-text('Submit PIN'), button[type='submit']"
    LOGIN_SUCCESS_INDICATOR = "text=Dashboard, text=My Bargains, //h1[contains(text(), 'Dashboard')]"
    
    async def login_with_mobile(self, mobile: str):
        """
        Enter mobile number and request OTP.
        
        Args:
            mobile: Mobile number (10 digits).
            
        Raises:
            ElementNotFoundException: If input fields not found.
        """
        logger.info(f"Logging in with mobile: [REDACTED]")
        try:
            await self.safe_type(self.MOBILE_INPUT, mobile)
            await self.safe_click(self.REQUEST_OTP_BTN)
            logger.info("OTP request sent")
        except Exception as e:
            logger.error(f"Failed to login with mobile: {e}")
            raise AuthenticationException("Failed to request OTP") from e
    
    async def submit_otp(self, otp: str):
        """
        Enter and submit OTP code.
        
        Args:
            otp: OTP code (6 digits).
        """
        logger.info(f"Submitting OTP: [REDACTED]")
        try:
            await self.safe_type(self.OTP_INPUT, otp)
            await self.safe_click(self.OTP_SUBMIT_BTN)
            logger.info("OTP submitted")
        except Exception as e:
            logger.error(f"Failed to submit OTP: {e}")
            raise AuthenticationException("Failed to submit OTP") from e
    
    async def submit_pin(self, pin: str):
        """
        Enter and submit PIN.
        
        Args:
            pin: PIN code (4 digits).
        """
        logger.info(f"Submitting PIN: [REDACTED]")
        try:
            await self.safe_type(self.PIN_INPUT, pin)
            await self.safe_click(self.PIN_SUBMIT_BTN)
            logger.info("PIN submitted")
        except Exception as e:
            logger.error(f"Failed to submit PIN: {e}")
            raise AuthenticationException("Failed to submit PIN") from e
    
    async def verify_login_success(self) -> bool:
        """
        Verify user is logged in (dashboard visible).
        
        Returns:
            bool: True if login successful.
        """
        logger.info("Verifying login success")
        try:
            element = await self.find_element(self.LOGIN_SUCCESS_INDICATOR)
            logger.info("Login successful - Dashboard visible")
            return element is not None
        except Exception as e:
            logger.error(f"Login verification failed: {e}")
            await self.take_screenshot("login_failed")
            raise ElementNotFoundException("Dashboard not found - login failed") from e
