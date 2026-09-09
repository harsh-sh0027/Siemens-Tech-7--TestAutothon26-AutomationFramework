"""Mobile website login page implementation (Appium + Android browser)."""

from src.pages.mobile.base_screen import BaseScreen
from src.pages.interfaces.login_page import ILoginPage
from src.utils.logger import StructuredLogger
from src.exceptions import ElementNotFoundException, AuthenticationException

logger = StructuredLogger.get_logger(__name__)


class MobileWebLoginPage(BaseScreen, ILoginPage):
    """Login workflow for the Gajab mobile website in Android Chrome."""

    MOBILE_INPUT = "css=input[placeholder*='Mobile'], input[name='mobile'], input[type='tel']"
    LOCATION_OVERLAY = "css=#location-fullscreen-click-blocker"
    LOGIN_ENTRY_BUTTON = "xpath=//button[contains(., 'Start Bargaining') or contains(., 'Login') or contains(., 'Sign in')] | //a[contains(., 'Start Bargaining') or contains(., 'Login') or contains(., 'Sign in')]"
    REQUEST_OTP_BTN = "xpath=//button[normalize-space()='Request OTP' or .//span[normalize-space()='Request OTP'] or .//*[normalize-space()='Request OTP']]"
    OTP_INPUT = "css=input[maxlength='6'], input[placeholder*='OTP'], input[inputmode='numeric']"
    OTP_SUBMIT_BTN = "xpath=//button[contains(., 'Verify OTP') or contains(., 'Submit') or @type='submit']"
    PIN_INPUT = "css=input[type='password'], input[placeholder*='PIN']"
    PIN_SUBMIT_BTN = "xpath=//button[contains(., 'Submit PIN') or contains(., 'Continue') or @type='submit']"
    LOGIN_SUCCESS_INDICATOR = "xpath=//*[contains(., 'Dashboard') or contains(., 'My Bargains')]"

    async def login_with_mobile(self, mobile: str):
        logger.info("Logging in to mobile website with mobile number: [REDACTED]")
        try:
            try:
                await self.find_element(self.MOBILE_INPUT)
            except Exception:
                logger.info("Mobile input not visible yet; opening login entry point")
                try:
                    await self.safe_click(self.LOGIN_ENTRY_BUTTON)
                except Exception:
                    logger.info("Login entry is blocked; dismissing location overlay and retrying")
                    await self.safe_click(self.LOCATION_OVERLAY)
                    await self.safe_click(self.LOGIN_ENTRY_BUTTON)

            await self.safe_type(self.MOBILE_INPUT, mobile)
            if self.driver.execute_script(
                "const btn = document.evaluate(arguments[0].replace('xpath=', ''), document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                "return !!(btn && btn.disabled);",
                self.REQUEST_OTP_BTN,
            ):
                logger.info("Request OTP is disabled; accepting consent checkbox")
                self.driver.execute_script(
                    "const checkbox = document.querySelector('input[type=\"checkbox\"]');"
                    "if (!checkbox) return false;"
                    "checkbox.click();"
                    "checkbox.dispatchEvent(new Event('input', {bubbles:true}));"
                    "checkbox.dispatchEvent(new Event('change', {bubbles:true}));"
                    "return checkbox.checked;"
                )
            await self.safe_click(self.REQUEST_OTP_BTN)
            logger.info("OTP request sent from mobile website")
        except Exception as e:
            logger.error(f"Failed to login with mobile website flow: {e}")
            raise AuthenticationException("Failed to request OTP on mobile website") from e

    async def submit_otp(self, otp: str):
        logger.info("Submitting OTP on mobile website: [REDACTED]")
        try:
            await self.safe_type(self.OTP_INPUT, otp)
            await self.safe_click(self.OTP_SUBMIT_BTN)
            logger.info("OTP submitted on mobile website")
        except Exception as e:
            logger.error(f"Failed to submit OTP on mobile website: {e}")
            raise AuthenticationException("Failed to submit OTP on mobile website") from e

    async def submit_pin(self, pin: str):
        logger.info("Submitting PIN on mobile website: [REDACTED]")
        try:
            await self.safe_type(self.PIN_INPUT, pin)
            await self.safe_click(self.PIN_SUBMIT_BTN)
            logger.info("PIN submitted on mobile website")
        except Exception as e:
            logger.error(f"Failed to submit PIN on mobile website: {e}")
            raise AuthenticationException("Failed to submit PIN on mobile website") from e

    async def verify_login_success(self) -> bool:
        logger.info("Verifying mobile website login success")
        try:
            element = await self.find_element(self.LOGIN_SUCCESS_INDICATOR)
            logger.info("Mobile website login successful")
            return element is not None
        except Exception as e:
            logger.error(f"Mobile website login verification failed: {e}")
            await self.take_screenshot('mobile_web_login_failed')
            raise ElementNotFoundException("Dashboard not found on mobile website") from e