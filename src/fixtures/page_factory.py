"""Page object factory — returns page implementations based on isMobile flag.

ONLY component (besides DriverFactory) allowed to branch on isMobile.
Tests use page interfaces ONLY, never concrete implementations.
"""

from src.utils.logger import StructuredLogger

logger = StructuredLogger.get_logger(__name__)


class PageObjectFactory:
    """
    Factory to return page implementations based on isMobile flag.
    
    CRITICAL: This is ONE of TWO places allowed to branch on isMobile.
    The other is DriverFactory.
    
    - Tests never check isMobile
    - Tests never instantiate page classes directly
    - Tests call factory.get_xxx_page() which returns interface
    - Factory returns Web or Mobile implementation
    """
    
    def __init__(self, driver, is_mobile: bool):
        """
        Initialize factory.
        
        Args:
            driver: IDriverProvider (Web or Mobile).
            is_mobile: Flag indicating platform (True = Appium, False = Playwright).
        """
        self.driver = driver
        self.is_mobile = is_mobile
        logger.info(f"PageObjectFactory initialized (isMobile={is_mobile})")
    
    def get_login_page(self):
        """
        Get LoginPage implementation.
        
        Returns:
            ILoginPage: WebLoginPage (if Web) or MobileLoginScreen (if Mobile).
        """
        if self.is_mobile:
            if getattr(self.driver, 'uses_browser', False):
                logger.debug("Returning MobileWebLoginPage")
                from src.pages.mobile.login_page_mobile_web import MobileWebLoginPage
                return MobileWebLoginPage(self.driver.get_driver(), is_mobile=True)

            logger.debug("Returning MobileLoginScreen")
            from src.pages.mobile.login_page_mobile import MobileLoginScreen
            return MobileLoginScreen(self.driver.get_driver(), is_mobile=True)
        else:
            logger.debug("Returning WebLoginPage")
            from src.pages.web.login_page_web import WebLoginPage
            return WebLoginPage(self.driver.get_page(), is_mobile=False)
