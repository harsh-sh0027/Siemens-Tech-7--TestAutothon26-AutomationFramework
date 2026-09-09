"""Centralized configuration — single source of truth for isMobile flag and all settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file once at module import
load_dotenv()


class ConfigLoader:
    """
    Centralized configuration loader.
    
    Reads environment variables and provides config values to the entire framework.
    The isMobile flag is read ONCE at session start and is immutable thereafter.
    Thread-safe: all static methods, no mutable state.
    """
    
    # ===== PLATFORM SELECTION (READ ONCE) =====
    @staticmethod
    def is_mobile() -> bool:
        """
        Returns True for Mobile (Appium), False for Web (Playwright).
        
        Set via: environment variable IS_MOBILE=true|false
        Read once at fixture scope; immutable thereafter.
        
        Returns:
            bool: True if running against Mobile, False for Web.
        """
        value = os.getenv('IS_MOBILE', 'false').lower()
        return value in ['true', '1', 'yes']
    
    # ===== APPLICATION URLS =====
    @staticmethod
    def base_url() -> str:
        """
        Gajab staging base URL.
        
        Returns:
            str: Base URL for Web tests.
        """
        return os.getenv('GAJAB_BASE_URL', 'https://stg.gajab.com')
    
    # ===== BROWSER/DRIVER CONFIG =====
    @staticmethod
    def browser() -> str:
        """
        Browser choice for Playwright.
        
        Returns:
            str: One of: chromium, firefox, webkit, edge.
        """
        return os.getenv('BROWSER', 'chromium')

    @staticmethod
    def browser_channel() -> str | None:
        """
        Optional browser channel for Chromium-based browsers.

        Returns:
            str | None: Browser channel (for example: msedge), else None.
        """
        value = os.getenv('BROWSER_CHANNEL', '').strip()
        return value or None
    
    @staticmethod
    def headless() -> bool:
        """
        Run browser in headless mode (no UI).
        
        Returns:
            bool: True for headless, False for headed.
        """
        return os.getenv('HEADLESS', 'false').lower() in ['true', '1']
    
    # ===== APPIUM CONFIG =====
    @staticmethod
    def appium_host() -> str:
        """
        Appium server host.
        
        Returns:
            str: Appium host (default: 127.0.0.1).
        """
        return os.getenv('APPIUM_HOST', '127.0.0.1')
    
    @staticmethod
    def appium_port() -> int:
        """
        Appium server port.
        
        Returns:
            int: Appium port (default: 4723).
        """
        return int(os.getenv('APPIUM_PORT', '4723'))
    
    @staticmethod
    def app_package() -> str:
        """
        Android app package name.
        
        Returns:
            str: Package name (e.g., com.example.gajab).
        """
        return os.getenv('APP_PACKAGE', 'com.example.gajab')
    
    @staticmethod
    def app_activity() -> str:
        """
        Android app main activity.
        
        Returns:
            str: Activity name (e.g., .MainActivity).
        """
        return os.getenv('APP_ACTIVITY', '.MainActivity')
    
    # ===== TEST DATA =====
    @staticmethod
    def test_mobile() -> str:
        """
        Synthetic test mobile number.
        
        Returns:
            str: Test mobile number (9999999999 by default).
        """
        return os.getenv('TEST_MOBILE', '9999999999')
    
    @staticmethod
    def test_otp() -> str:
        """
        Test OTP value (synthetic, organizer-provided).
        
        Returns:
            str: Test OTP code.
        """
        return os.getenv('TEST_OTP', '123456')
    
    @staticmethod
    def test_pin() -> str:
        """
        Test PIN value (synthetic).
        
        Returns:
            str: Test PIN code.
        """
        return os.getenv('TEST_PIN', '1234')

    @staticmethod
    def challenge_language() -> str:
        """
        Preferred UI language for the workflow.

        Returns:
            str: english or hinglish.
        """
        return os.getenv('CHALLENGE_LANGUAGE', 'english').strip().lower()

    @staticmethod
    def results_email() -> str:
        """
        Authorized email recipient for challenge artifacts.

        Returns:
            str: Email address or empty string when unavailable.
        """
        return os.getenv('RESULTS_EMAIL', '').strip()

    @staticmethod
    def challenge_data_path() -> str:
        """
        Excel workbook containing workflow test data and fallbacks.

        Returns:
            str: Absolute path to the workbook.
        """
        configured = os.getenv('CHALLENGE_DATA_PATH', '').strip()
        if configured:
            return configured
        root_dir = Path(__file__).resolve().parents[2]
        return str(root_dir / 'src' / 'test' / 'python' / 'resources' / 'challenge_data.xlsx')

    @staticmethod
    def allow_fallbacks() -> bool:
        """
        Control whether tests may use documented fallbacks for unavailable live data.

        Returns:
            bool: True when fallback behavior is allowed.
        """
        return os.getenv('ALLOW_FALLBACKS', 'true').lower() in ['true', '1', 'yes']
    
    # ===== TIMEOUTS (seconds) =====
    @staticmethod
    def explicit_wait_timeout() -> int:
        """
        Default explicit wait timeout in seconds.
        
        Used by WaitUtilities for condition-based waits.
        
        Returns:
            int: Timeout in seconds (default: 10).
        """
        return int(os.getenv('EXPLICIT_WAIT_TIMEOUT', '10'))
    
    @staticmethod
    def page_load_timeout() -> int:
        """
        Page load timeout in seconds.
        
        Used by driver for navigation waits.
        
        Returns:
            int: Timeout in seconds (default: 15).
        """
        return int(os.getenv('PAGE_LOAD_TIMEOUT', '15'))
    
    @staticmethod
    def poll_interval() -> float:
        """
        Polling interval in seconds for wait conditions.
        
        Controls how often WaitUtilities check for conditions.
        NO hardcoded sleeps; all waits use this config value.
        
        Returns:
            float: Poll interval in seconds (default: 0.5).
        """
        return float(os.getenv('POLL_INTERVAL', '0.5'))
    
    # ===== LOGGING =====
    @staticmethod
    def log_level() -> str:
        """
        Logger level (DEBUG, INFO, WARN, ERROR).
        
        Returns:
            str: Log level (default: INFO).
        """
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def log_dir() -> str:
        """
        Directory for log files.
        
        Returns:
            str: Log directory path.
        """
        return os.getenv('LOG_DIR', './logs')
    
    @staticmethod
    def screenshots_dir() -> str:
        """
        Directory for screenshots and diagnostics.
        
        Returns:
            str: Screenshots directory path.
        """
        return os.getenv('SCREENSHOTS_DIR', './reports/screenshots')
