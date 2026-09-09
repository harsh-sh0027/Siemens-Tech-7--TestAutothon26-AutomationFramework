"""Mobile login screen implementation (Appium)."""

from src.pages.mobile.base_screen import BaseScreen
from src.pages.interfaces.login_page import ILoginPage
from src.utils.logger import StructuredLogger
from src.utils.config import ConfigLoader
from src.exceptions import ElementNotFoundException, AuthenticationException

logger = StructuredLogger.get_logger(__name__)


class MobileLoginScreen(BaseScreen, ILoginPage):
    """
    Login screen for Mobile (Appium).
    
    Implements ILoginPage interface using Appium-based interactions.
    Locators and interaction details specific to Mobile platform.
    """
    
    @staticmethod
    def _id(resource_name: str) -> str:
        return f"id={ConfigLoader.app_package()}:id/{resource_name}"
    
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
            await self.safe_type(self._id('mobile_input'), mobile)
            await self.safe_click(self._id('request_otp_btn'))
            logger.info("OTP request sent")
        except Exception as e:
            logger.error(f"Failed to login with mobile: {e}")
            await self.take_screenshot("login_failed")
            raise AuthenticationException("Failed to request OTP") from e
    
    async def submit_otp(self, otp: str):
        """
        Enter and submit OTP code.
        
        Args:
            otp: OTP code (6 digits).
        """
        logger.info(f"Submitting OTP: [REDACTED]")
        try:
            await self.safe_type(self._id('otp_input'), otp)
            await self.safe_click(self._id('verify_otp_btn'))
            logger.info("OTP submitted")
        except Exception as e:
            logger.error(f"Failed to submit OTP: {e}")
            await self.take_screenshot("otp_failed")
            raise AuthenticationException("Failed to submit OTP") from e
    
    async def submit_pin(self, pin: str):
        """
        Enter and submit PIN.
        
        Args:
            pin: PIN code (4 digits).
        """
        logger.info(f"Submitting PIN: [REDACTED]")
        try:
            await self.safe_type(self._id('pin_input'), pin)
            await self.safe_click(self._id('submit_pin_btn'))
            logger.info("PIN submitted")
        except Exception as e:
            logger.error(f"Failed to submit PIN: {e}")
            await self.take_screenshot("pin_failed")
            raise AuthenticationException("Failed to submit PIN") from e
    
    async def verify_login_success(self) -> bool:
        """
        Verify user is logged in (dashboard visible).
        
        Returns:
            bool: True if login successful.
        """
        logger.info("Verifying login success")
        try:
            element = await self.find_element(self._id('dashboard_title'))
            logger.info("Login successful - Dashboard visible")
            return element is not None
        except Exception as e:
            logger.error(f"Login verification failed: {e}")
            await self.take_screenshot("login_verification_failed")
            raise ElementNotFoundException("Dashboard not found - login failed") from e
