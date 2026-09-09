"""Custom exception hierarchy for Gajab automation framework.

All driver exceptions are caught at the utility layer and translated to these
custom exceptions with descriptive context (page, locator, action).
"""


class AutomationException(Exception):
    """Base exception for all automation-related errors."""
    pass


class ElementNotFoundException(AutomationException):
    """Raised when element is not found or not visible within timeout."""
    pass


class PageLoadTimeoutException(AutomationException):
    """Raised when page does not load or element does not become visible within timeout."""
    pass


class OffersMaxAttemptsExceededException(AutomationException):
    """Raised when bargaining max attempts (3) exceeded without acceptance."""
    pass


class PaymentGatewayException(AutomationException):
    """Raised when payment gateway redirect fails or URL validation fails."""
    pass


class AuthenticationException(AutomationException):
    """Raised when login, OTP, or PIN flow fails."""
    pass


class AppiumConnectionException(AutomationException):
    """Raised when Appium server connection fails."""
    pass


class DriverInitException(AutomationException):
    """Raised when WebDriver or Appium driver initialization fails."""
    pass
