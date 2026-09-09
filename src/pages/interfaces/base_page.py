"""Abstract base interface for all page objects.

All pages (Web and Mobile) implement these common methods.
"""

from abc import ABC, abstractmethod


class IBasePage(ABC):
    """
    Common interface for all pages (Web and Mobile implementations).
    
    Defines contract for basic page operations.
    Each workflow gets a separate interface extending this (e.g., ILoginPage).
    """
    
    @abstractmethod
    def get_page(self):
        """
        Return driver/page object.
        
        For advanced operations when page-specific methods are insufficient.
        
        Returns:
            Playwright Page or Appium WebDriver.
        """
        raise NotImplementedError
    
    @abstractmethod
    def navigate_to(self, url: str = None):
        """
        Navigate to URL (Web) or launch app (Mobile).
        
        Args:
            url: URL to navigate to (Web only, None for Mobile).
        """
        raise NotImplementedError
