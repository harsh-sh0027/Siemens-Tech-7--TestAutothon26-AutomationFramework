"""Web login page implementation (Playwright)."""

from urllib.parse import urljoin

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
    
    OPEN_LOGIN_CTA = [
        "a:has-text('Log in / Sign up')",
        "button:has-text('Log in / Sign up')",
        "text=Log in / Sign up",
        "a[href*='signin']",
        "a[href*='auth']",
    ]
    MOBILE_INPUTS = [
        "input[placeholder*='Mobile Number']",
        "input[placeholder*='Mobile']",
        "input[placeholder*='Phone']",
        "input[placeholder*='number']",
        "input[name='mobile']",
        "input[name*='phone']",
        "input[id*='mobile']",
        "input[type='tel']",
        "input[maxlength='10']",
        "form input[type='text']",
        "#mobile-input",
    ]
    REQUEST_OTP_BTNS = [
        "button:has-text('Request OTP')",
        "button:has-text('Get OTP')",
        "button:has-text('Send OTP')",
        "button[type='submit']",
    ]
    TERMS_CHECKBOXES = [
        "#signin-terms-checkbox",
        "input[type='checkbox'][id*='terms']",
        "label:has-text('Terms') input[type='checkbox']",
        "label:has-text('I agree') input[type='checkbox']",
    ]
    OTP_SINGLE_INPUTS = [
        "#signin-otp-input",
        "input[name*='otp']",
        "input[maxlength='6']",
        "input[placeholder*='OTP']",
        "input[placeholder*='Enter OTP']",
        "#otp-input",
    ]
    OTP_DIGIT_INPUTS = [
        "input[id^='otp-input-']",
        "input[aria-label*='OTP']",
        "input[inputmode='numeric']",
        "form input[type='text']",
        "form input[type='number']",
    ]
    OTP_SUBMIT_BTNS = [
        "button:has-text('Submit')",
        "button:has-text('Verify OTP')",
        "button:has-text('Verify')",
        "button[type='submit']",
    ]
    PIN_INPUTS = [
        "input[placeholder*='PIN']",
        "input[placeholder*='Pin']",
        "input[type='password']",
        "input[placeholder*='Pincode']",
        "input[placeholder*='Pincode or City']",
    ]
    PIN_SUBMIT_BTNS = [
        "button:has-text('Submit PIN')",
        "button:has-text('Submit')",
        "button:has-text('Continue')",
        "button[type='submit']",
    ]
    PINCODE_SUGGESTION = [
        "li:has-text('560037')",
        "text=560037",
        "[role='option']:has-text('560037')",
    ]
    LOGIN_SUCCESS_INDICATORS = [
        "text=My Bargains",
        "text=Trending",
        "text=Just Bargained",
        "a:has-text('My Bargains')",
        "button:has-text('My Bargains')",
    ]

    async def _ensure_login_form_visible(self):
        """Open login dialog/page when mobile field is not immediately visible."""
        try:
            await self.find_first_visible(self.MOBILE_INPUTS, timeout=2)
            return
        except Exception:
            pass

        await self.dismiss_common_popups()
        try:
            await self.safe_click_any(self.OPEN_LOGIN_CTA, timeout=6)
        except Exception:
            logger.warning("Login CTA click failed; trying direct signin navigation")

        try:
            await self.find_first_visible(self.MOBILE_INPUTS, timeout=8)
            return
        except Exception:
            pass

        signin_url = urljoin(self.page.url, "/auth/signin")
        logger.info(f"Falling back to direct signin URL: {signin_url}")
        await self.navigate_to(signin_url)
        await self.dismiss_common_popups()
        await self.find_first_visible(self.MOBILE_INPUTS, timeout=12)
    
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
            await self.dismiss_common_popups()
            await self._ensure_login_form_visible()
            await self.safe_type_any(self.MOBILE_INPUTS, mobile, timeout=10)

            # Some login variants require explicit terms acceptance.
            for selector in self.TERMS_CHECKBOXES:
                try:
                    checkbox = self.page.locator(selector).first
                    if await checkbox.is_visible(timeout=1000):
                        if not await checkbox.is_checked():
                            await checkbox.check(force=True)
                        break
                except Exception:
                    continue

            await self.safe_click_any(self.REQUEST_OTP_BTNS, timeout=8)
            logger.info("OTP request sent")
        except Exception as e:
            logger.error(f"Failed to login with mobile: {e}")
            await self.take_screenshot("login_mobile_failed")
            raise AuthenticationException("Failed to request OTP") from e
    
    async def submit_otp(self, otp: str):
        """
        Enter and submit OTP code.
        
        Args:
            otp: OTP code (6 digits).
        """
        logger.info(f"Submitting OTP: [REDACTED]")
        try:
            await self.dismiss_common_popups()

            # If OTP field didn't render after request, click request again once.
            try:
                await self.find_first_visible(self.OTP_SINGLE_INPUTS + self.OTP_DIGIT_INPUTS, timeout=3)
            except Exception:
                try:
                    await self.safe_click_any(self.REQUEST_OTP_BTNS, timeout=2)
                except Exception:
                    pass
                await self.dismiss_common_popups()

            # Variant 1: single OTP input
            single_filled = False
            for selector in self.OTP_SINGLE_INPUTS:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.is_visible(timeout=1200):
                        max_length = await locator.get_attribute("maxlength")
                        if max_length == "1":
                            # This is a per-digit box; handle in digit-input flow.
                            continue
                        await locator.fill(otp)
                        single_filled = True
                        break
                except Exception:
                    pass

            # Variant 2: one input per OTP digit
            if not single_filled:
                digit_inputs = None
                for selector in self.OTP_DIGIT_INPUTS:
                    candidate = self.page.locator(selector)
                    try:
                        count = await candidate.count()
                        if count >= 4:
                            digit_inputs = candidate
                            break
                    except Exception:
                        pass

                if digit_inputs is None:
                    raise AuthenticationException("OTP input fields were not found")

                otp_digits = list(otp.strip())
                digit_count = min(await digit_inputs.count(), len(otp_digits))
                for index in range(digit_count):
                    field = digit_inputs.nth(index)
                    if not await field.is_visible(timeout=1200):
                        break
                    await field.click(force=True)
                    await field.fill(otp_digits[index])

            # Some flows auto-authenticate right after OTP typing.
            if "/seller" in self.page.url or "/auth" not in self.page.url:
                logger.info("OTP accepted with auto-navigation; explicit submit not required")
                return

            try:
                await self.safe_click_any(self.OTP_SUBMIT_BTNS, timeout=6)
            except Exception as submit_error:
                # Recover if auth completed while submit became detached/disabled.
                if "/seller" in self.page.url or "/auth" not in self.page.url:
                    logger.info("OTP submit click failed but session navigated; treating as success")
                    return

                try:
                    await self.find_first_visible(self.LOGIN_SUCCESS_INDICATORS, timeout=4)
                    logger.info("OTP submit click failed but login indicators found; treating as success")
                    return
                except Exception:
                    raise submit_error

            logger.info("OTP submitted")
        except Exception as e:
            logger.error(f"Failed to submit OTP: {e}")
            await self.take_screenshot("otp_submit_failed")
            raise AuthenticationException("Failed to submit OTP") from e
    
    async def submit_pin(self, pin: str):
        """
        Enter and submit PIN.
        
        Args:
            pin: PIN code (4 digits).
        """
        logger.info(f"Submitting PIN: [REDACTED]")
        try:
            await self.dismiss_common_popups()

            # In some live builds, OTP directly signs in and this step is skipped.
            try:
                await self.find_first_visible(self.LOGIN_SUCCESS_INDICATORS, timeout=3)
                logger.info("PIN step not required in current flow; already signed in")
                return
            except Exception:
                pass

            selected = await self.safe_type_any(self.PIN_INPUTS, pin, timeout=6)

            # Pincode field often requires selecting a suggestion.
            if "Pincode" in selected or "pincode" in selected:
                try:
                    await self.safe_click_any(self.PINCODE_SUGGESTION, timeout=4)
                except Exception:
                    logger.info("Pincode suggestion not shown; continuing")

            try:
                await self.safe_click_any(self.PIN_SUBMIT_BTNS, timeout=4)
            except Exception:
                logger.info("No explicit PIN submit button found; continuing")

            logger.info("PIN submitted")
        except Exception as e:
            logger.error(f"Failed to submit PIN: {e}")
            # Fallback: do not fail if login is already successful after OTP.
            try:
                await self.find_first_visible(self.LOGIN_SUCCESS_INDICATORS, timeout=4)
                logger.info("PIN submission failed but session appears authenticated; continuing")
                return
            except Exception:
                raise AuthenticationException("Failed to submit PIN") from e
    
    async def verify_login_success(self) -> bool:
        """
        Verify user is logged in (dashboard visible).
        
        Returns:
            bool: True if login successful.
        """
        logger.info("Verifying login success")
        try:
            await self.dismiss_common_popups()
            _, element = await self.find_first_visible(self.LOGIN_SUCCESS_INDICATORS, timeout=12)
            logger.info("Login successful - Dashboard visible")
            return element is not None
        except Exception as e:
            logger.error(f"Login verification failed: {e}")
            await self.take_screenshot("login_failed")
            raise ElementNotFoundException("Dashboard not found - login failed") from e
