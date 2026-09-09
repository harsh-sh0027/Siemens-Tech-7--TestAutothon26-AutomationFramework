"""Mobile login screen implementation (Appium)."""

from src.pages.mobile.base_screen import BaseScreen
from src.pages.interfaces.login_page import ILoginPage
from src.utils.logger import StructuredLogger
from src.exceptions import ElementNotFoundException, AuthenticationException

logger = StructuredLogger.get_logger(__name__)


class MobileLoginScreen(BaseScreen, ILoginPage):
    """
    Login screen for Mobile (Appium).
    
    Implements ILoginPage interface using Appium-based interactions.
    Locators and interaction details specific to Mobile platform.
    """
    
    # Locators (resource IDs for Android)
    # These are example locators; adjust per actual app structure
    MOBILE_INPUT = "com.example.gajab:id/mobile_input"
    REQUEST_OTP_BTN = "com.example.gajab:id/request_otp_btn"
    OTP_INPUT = "com.example.gajab:id/otp_input"
    OTP_SUBMIT_BTN = "com.example.gajab:id/verify_otp_btn"
    PIN_INPUT = "com.example.gajab:id/pin_input"
    PIN_SUBMIT_BTN = "com.example.gajab:id/submit_pin_btn"
    LOGIN_SUCCESS_INDICATOR = "com.example.gajab:id/dashboard_title"
    
    def login_with_mobile(self, mobile: str):
        """
        Enter mobile number and request OTP.
        
        Args:
            mobile: Mobile number (10 digits).
            
        Raises:
            ElementNotFoundException: If input fields not found.
        """
        logger.info(f"Logging in with mobile: [REDACTED]")
        try:
            self.safe_type(self.MOBILE_INPUT, mobile)
            self.safe_click(self.REQUEST_OTP_BTN)
            logger.info("OTP request sent")
        except Exception as e:
            logger.error(f"Failed to login with mobile: {e}")
            self.take_screenshot("login_failed")
            raise AuthenticationException("Failed to request OTP") from e
    
    def submit_otp(self, otp: str):
        """
        Enter and submit OTP code.
        
        Args:
            otp: OTP code (6 digits).
        """
        logger.info(f"Submitting OTP: [REDACTED]")
        try:
            self.safe_type(self.OTP_INPUT, otp)
            self.safe_click(self.OTP_SUBMIT_BTN)
            logger.info("OTP submitted")
        except Exception as e:
            logger.error(f"Failed to submit OTP: {e}")
            self.take_screenshot("otp_failed")
            raise AuthenticationException("Failed to submit OTP") from e
    
    def submit_pin(self, pin: str):
        """
        Enter and submit PIN.
        
        Args:
            pin: PIN code (4 digits).
        """
        logger.info(f"Submitting PIN: [REDACTED]")
        try:
            self.safe_type(self.PIN_INPUT, pin)
            self.safe_click(self.PIN_SUBMIT_BTN)
            logger.info("PIN submitted")
        except Exception as e:
            logger.error(f"Failed to submit PIN: {e}")
            self.take_screenshot("pin_failed")
            raise AuthenticationException("Failed to submit PIN") from e
    
    def verify_login_success(self) -> bool:
        """
        Verify user is logged in (dashboard visible).
        
        Returns:
            bool: True if login successful.
        """
        logger.info("Verifying login success")
        try:
            element = self.find_element(self.LOGIN_SUCCESS_INDICATOR)
            logger.info("Login successful - Dashboard visible")
            return element is not None
        except Exception as e:
            logger.error(f"Login verification failed: {e}")
            self.take_screenshot("login_verification_failed")
            raise ElementNotFoundException("Dashboard not found - login failed") from e
