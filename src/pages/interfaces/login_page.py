"""Login workflow interface.

Defines contract for login functionality (OTP + PIN flow).
Implemented by WebLoginPage and MobileLoginScreen.
"""

from abc import ABC, abstractmethod


class ILoginPage(ABC):
    """
    Login workflow interface.
    
    Defines multi-step authentication flow:
    1. Enter mobile number
    2. Request OTP
    3. Enter OTP
    4. Enter PIN
    5. Verify success
    
    Both Web and Mobile implement this interface exactly.
    """
    
    @abstractmethod
    def login_with_mobile(self, mobile: str):
        """
        Enter mobile number and request OTP.
        
        Args:
            mobile: Mobile number (10 digits).
            
        Raises:
            ElementNotFoundException: If input field not found.
            AuthenticationException: If OTP request fails.
        """
        raise NotImplementedError
    
    @abstractmethod
    def submit_otp(self, otp: str):
        """
        Enter and submit OTP code.
        
        Args:
            otp: OTP code (6 digits).
            
        Raises:
            ElementNotFoundException: If OTP input not found.
            AuthenticationException: If OTP submission fails.
        """
        raise NotImplementedError
    
    @abstractmethod
    def submit_pin(self, pin: str):
        """
        Enter and submit PIN.
        
        Args:
            pin: PIN code (4 digits).
            
        Raises:
            ElementNotFoundException: If PIN input not found.
            AuthenticationException: If PIN submission fails.
        """
        raise NotImplementedError
    
    @abstractmethod
    def verify_login_success(self) -> bool:
        """
        Verify user is logged in (dashboard visible).
        
        Returns:
            bool: True if login successful.
            
        Raises:
            ElementNotFoundException: If dashboard element not found.
        """
        raise NotImplementedError
