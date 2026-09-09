# Gajab Automation Framework — TestAutothon 2026

A unified, reusable test automation framework for Web (Playwright) and Mobile (Appium) platforms. Same test code runs on both platforms via single `isMobile` configuration flag.

## Quick Start

### Prerequisites
- Python 3.9+
- Playwright browsers (auto-installed)
- Appium server (for mobile testing)
- Android SDK (for Appium mobile testing)

### Setup

```bash
# 1. Clone and navigate
cd Siemens-Tech-7--TestAutothon26-AutomationFramework

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
python -m playwright install

# 5. Copy .env template and configure
cp .env.example .env
# Edit .env to set IS_MOBILE, GAJAB_BASE_URL, Appium settings, etc.
```

### Run Tests

#### Web Mode (Playwright)
```bash
pytest src/test/python/tests/ -v
# or explicitly:
pytest src/test/python/tests/ -v --isMobile=false
```

#### Mobile Mode (Appium)
```bash
# Start Appium server first
appium

# In another terminal:
pytest src/test/python/tests/ -v --isMobile
```

#### Parallel Execution
```bash
pytest src/test/python/tests/ -v -n 4  # 4 workers
```

#### Single Test
```bash
pytest src/test/python/tests/test_login.py::TestLogin::test_login_valid_credentials -v
```

#### Browser and Device-Size from CLI
```bash
# Browser selection
pytest src/test/python/tests/ -v --browser chromium
pytest src/test/python/tests/ -v --browser chrome
pytest src/test/python/tests/ -v --browser firefox
pytest src/test/python/tests/ -v --browser webkit
pytest src/test/python/tests/ -v --browser edge --browser-channel msedge

# Desktop viewport size
pytest src/test/python/tests/ -v --browser chromium --viewport 1920x1080

# Playwright device emulation
pytest src/test/python/tests/ -v --browser chromium --device "iPhone 13"
pytest src/test/python/tests/ -v --browser chromium --device "Pixel 5"

# Force headed/headless
pytest src/test/python/tests/ -v --headed
pytest src/test/python/tests/ -v --headless
```

#### Keyword Runner (Very Short Commands)
Use one command wrapper file with predefined keywords so you do not type long commands:

```powershell
# List available keywords
./run-keyword.ps1 -List

# Common runs
./run-keyword.ps1 chrome
./run-keyword.ps1 firefox
./run-keyword.ps1 webkit
./run-keyword.ps1 edge
./run-keyword.ps1 iphone13
./run-keyword.ps1 pixel5
./run-keyword.ps1 ipad
./run-keyword.ps1 mobile

# Add extra pytest args
./run-keyword.ps1 chrome -PytestArgs "--collect-only"

# Run a specific file with a keyword profile
./run-keyword.ps1 firefox -TestPath src/test/python/tests/test_login.py

# Override headed/headless for any keyword
./run-keyword.ps1 iphone13 -Headed
./run-keyword.ps1 chrome -Headless
```

### Reports Per Run

Every pytest run now creates a unique timestamped folder under `reports/runs/<YYYYMMDD-HHMMSS>/` with:

- `index.html` (run dashboard with links to all artifacts)
- `report.html` (pytest-html, self-contained)
- `junit.xml` (JUnit format for CI)
- `report.json` (machine-readable summary)
- `allure-results/` (raw Allure artifacts)
- `playwright-traces/` (Playwright built-in trace ZIP files)
- `screenshots/` (failure screenshots captured by hooks)

Example run command:

```bash
pytest src/test/python/tests/test_login.py::TestLogin::test_login_invalid_otp -v
```

Optional: generate a browsable Allure report (requires Allure CLI):

```bash
allure serve reports/runs/<RUN_ID>/allure-results
```

Playwright built-in HTML investigation path:

```bash
playwright show-trace reports/runs/<RUN_ID>/playwright-traces/<test-name>.zip
```

---

## Directory Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Locked dependency versions
├── .env.example                       # Environment config template
├── .env                               # (git-ignored) Actual config
├── .gitignore                         # Secure files/dirs
├── conftest.py                        # pytest fixtures & hooks
│
├── docs/
│   ├── architecture-design.md         # Architecture contract
│   ├── application-map.md             # App structure
│   ├── locator-inventory.md           # All element selectors
│   └── ...
│
├── logs/                              # (git-ignored) Test logs
│   └── run-YYYYMMDD-HHMMSS.log
│
├── reports/                           # (git-ignored) Test reports
│   ├── screenshots/                   # Failure screenshots
│   └── diagnostics/                   # Page source & logcat
│
└── src/
    ├── __init__.py
    │
    ├── utils/
    │   ├── __init__.py
    │   ├── config.py                  # ConfigLoader (reads isMobile)
    │   ├── logger.py                  # StructuredLogger with correlation ID
    │   ├── waits.py                   # WaitUtilities (no hardcoded sleeps)
    │
    ├── exceptions/
    │   └── __init__.py                # Custom exception hierarchy
    │
    ├── fixtures/
    │   ├── __init__.py
    │   ├── driver_factory.py          # DriverFactory (creates Web or Mobile driver)
    │   └── page_factory.py            # PageObjectFactory (returns page implementations)
    │
    ├── pages/
    │   ├── __init__.py
    │   │
    │   ├── interfaces/                # Page interfaces (business contracts)
    │   │   ├── __init__.py
    │   │   ├── base_page.py           # IBasePage (common interface)
    │   │   └── login_page.py          # ILoginPage (workflow interface)
    │   │
    │   ├── web/                       # Web implementations (Playwright)
    │   │   ├── __init__.py
    │   │   ├── base_page_web.py       # BasePage (common Web behavior)
    │   │   └── login_page_web.py      # WebLoginPage (Web login)
    │   │
    │   └── mobile/                    # Mobile implementations (Appium)
    │       ├── __init__.py
    │       ├── base_screen.py         # BaseScreen (common Mobile behavior)
    │       └── login_page_mobile.py   # MobileLoginScreen (Mobile login)
    │
    └── test/
        ├── __init__.py
        └── python/
            ├── tests/
            │   ├── __init__.py
            │   ├── test_login.py      # Example: Login tests
            │   ├── test_product.py    # (to-do) Product workflow tests
            │   └── ...
            └── resources/             # Test data, fixtures
```

---

## Architecture Overview

### The isMobile Flag: Single Source of Truth

```
┌─────────────────────────────────────────────────────────────────┐
│ conftest.py                                                      │
│                                                                  │
│  @fixture(scope="session")                                       │
│  def is_mobile():                                                │
│      # Read ONCE from:                                           │
│      # 1. CLI: pytest --isMobile                                 │
│      # 2. Env: IS_MOBILE=true                                    │
│      # 3. Default: false                                         │
│      return ConfigLoader.is_mobile()                             │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                ┌───────────────┴───────────────┐
                ↓                               ↓
        ┌──────────────────┐          ┌─────────────────┐
        │ DriverFactory    │          │ PageObjectFactory
        │                  │          │                 │
        │ BRANCHES on      │          │ BRANCHES on     │
        │ isMobile ONLY    │          │ isMobile ONLY   │
        └──────────────────┘          └─────────────────┘
                ↓                               ↓
        ┌──────────────────┐          ┌─────────────────┐
        │ PlaywrightDriver │          │ WebLoginPage    │
        │ OR AppiumDriver  │          │ OR MobileLogin  │
        └──────────────────┘          │ Screen          │
                                      └─────────────────┘
                                              ↓
                                ┌─────────────┴──────────────┐
                                ↓                            ↓
                        ┌──────────────────┐      ┌─────────────────┐
                        │ ILoginPage       │      │ Test Code       │
                        │                  │      │                 │
                        │ Implemented by:  │      │ Uses ONLY:      │
                        │ - WebLoginPage   │      │ - Interfaces    │
                        │ - MobileLogin    │      │ - Factories     │
                        │   Screen         │      │ - Utils         │
                        └──────────────────┘      │                 │
                                                  │ Never checks    │
                                                  │ isMobile!       │
                                                  └─────────────────┘
```

**Critical Constraint**: Only 2 components check `isMobile`:
1. **DriverFactory** — creates Web driver or Appium driver
2. **PageObjectFactory** — returns Web page or Mobile screen implementation

All other code (tests, pages, utilities) is completely platform-agnostic.

### Component Responsibilities

#### ConfigLoader (`src/utils/config.py`)
- Reads environment variables (`.env` file)
- Provides single source of truth for all config values
- Particularly: `is_mobile()` flag read once at session start
- Thread-safe: all static methods, no mutable state

#### StructuredLogger (`src/utils/logger.py`)
- Logs to `logs/run-YYYYMMDD-HHMMSS.log`
- **Correlation ID**: Every log line tagged with `[test-name-worker-id]`
- **PII Redaction**: Masks passwords, OTPs, mobile numbers, tokens before logging
- Used by all framework components for visibility

#### WaitUtilities (`src/utils/waits.py`)
- **NO hardcoded sleeps** anywhere
- All timeouts/poll intervals from config
- Implements: `wait_for_visible`, `wait_for_clickable`, `wait_for_invisible`, `wait_for_text_present`, `wait_for_loading_complete`
- Translates raw driver exceptions → custom exceptions (with context)

#### DriverFactory (`src/fixtures/driver_factory.py`)
- Creates WebDriver (Playwright) or Appium driver based on `is_mobile` flag
- Only component allowed to branch on `isMobile` (besides PageObjectFactory)
- Returns `IDriverProvider` abstraction (Web or Mobile wrapper)
- Handles lifecycle (initialization + async/sync)

#### PageObjectFactory (`src/fixtures/page_factory.py`)
- Returns page implementations based on `is_mobile` flag
- Only component allowed to branch on `isMobile` (besides DriverFactory)
- Test calls: `factory.get_login_page()` → returns `ILoginPage` (Web or Mobile)
- Tests depend on interfaces, never concrete implementations

#### Page Interfaces (`src/pages/interfaces/`)
- Small, focused contracts (ISP — Interface Segregation Principle)
- Example: `ILoginPage` with methods: `login_with_mobile()`, `submit_otp()`, `submit_pin()`, `verify_login_success()`
- Both Web and Mobile implementations implement same interface

#### Web Pages (`src/pages/web/`)
- **BasePage**: Common Playwright behavior (safe_click, safe_type, navigate, etc.)
- **WebLoginPage**: Implements `ILoginPage` with Web-specific selectors
- Web-specific locators (CSS selectors, XPath with `text=`)

#### Mobile Screens (`src/pages/mobile/`)
- **BaseScreen**: Common Appium behavior (safe_click, safe_type, swipe, etc.)
- **MobileLoginScreen**: Implements `ILoginPage` with Mobile-specific locators
- Mobile-specific locators (resource IDs, content descriptions)

#### Test Layer (`src/test/python/tests/`)
- **TestLogin**: Tests implement test methods against page interfaces ONLY
- Same test code runs for Web and Mobile (isMobile flag switches implementation)
- Example: `test_login_valid_credentials()` doesn't know or care about platform

---

## Adding a New Page/Workflow

Follow this pattern to add a new page (e.g., ProductPage):

### 1. Create Interface
File: `src/pages/interfaces/product_page.py`

```python
from abc import ABC, abstractmethod

class IProductPage(ABC):
    """Product page interface — business contract."""
    
    @abstractmethod
    def get_product_list(self) -> list:
        """Get list of products."""
        pass
    
    @abstractmethod
    def select_product(self, product_id: str):
        """Select product by ID."""
        pass
    
    @abstractmethod
    def verify_product_details(self, name: str) -> bool:
        """Verify product details are visible."""
        pass
```

### 2. Implement for Web
File: `src/pages/web/product_page_web.py`

```python
from src.pages.web.base_page_web import BasePage
from src.pages.interfaces.product_page import IProductPage
from src.utils.logger import StructuredLogger

logger = StructuredLogger.get_logger(__name__)

class WebProductPage(BasePage, IProductPage):
    """Product page for Web (Playwright)."""
    
    # Web-specific selectors
    PRODUCT_LIST = "div[class*='product-item']"
    PRODUCT_NAME = "//div[@class='product-card']/h3"
    
    def get_product_list(self) -> list:
        logger.info("Getting product list (Web)")
        # Playwright implementation
        pass
    
    def select_product(self, product_id: str):
        logger.info(f"Selecting product: {product_id} (Web)")
        pass
    
    def verify_product_details(self, name: str) -> bool:
        logger.info(f"Verifying product details: {name} (Web)")
        pass
```

### 3. Implement for Mobile
File: `src/pages/mobile/product_page_mobile.py`

```python
from src.pages.mobile.base_screen import BaseScreen
from src.pages.interfaces.product_page import IProductPage
from src.utils.logger import StructuredLogger

logger = StructuredLogger.get_logger(__name__)

class MobileProductScreen(BaseScreen, IProductPage):
    """Product screen for Mobile (Appium)."""
    
    # Mobile-specific selectors (resource IDs)
    PRODUCT_LIST = "com.example.gajab:id/product_list"
    PRODUCT_ITEM = "com.example.gajab:id/product_item"
    
    def get_product_list(self) -> list:
        logger.info("Getting product list (Mobile)")
        # Appium implementation
        pass
    
    def select_product(self, product_id: str):
        logger.info(f"Selecting product: {product_id} (Mobile)")
        pass
    
    def verify_product_details(self, name: str) -> bool:
        logger.info(f"Verifying product details: {name} (Mobile)")
        pass
```

### 4. Update PageObjectFactory
File: `src/fixtures/page_factory.py`

```python
def get_product_page(self):
    """Get ProductPage implementation."""
    if self.is_mobile:
        logger.debug("Returning MobileProductScreen")
        from src.pages.mobile.product_page_mobile import MobileProductScreen
        return MobileProductScreen(self.driver.get_driver(), is_mobile=True)
    else:
        logger.debug("Returning WebProductPage")
        from src.pages.web.product_page_web import WebProductPage
        return WebProductPage(self.driver.get_page(), is_mobile=False)
```

### 5. Write Tests
File: `src/test/python/tests/test_product.py`

```python
class TestProduct:
    """Product workflow tests."""
    
    def test_view_product_details(self, page_factory, driver):
        """Same test runs for Web and Mobile."""
        product_page = page_factory.get_product_page()
        
        if not driver.is_mobile:
            product_page.navigate_to(ConfigLoader.base_url() + "/products")
        
        products = product_page.get_product_list()
        assert len(products) > 0, "No products found"
        
        # Test passes for both Web and Mobile!
```

---

## Configuration

### Environment Variables (`.env`)

```env
# Platform selection
IS_MOBILE=false  # Set to true for Appium/Mobile

# Web settings
BROWSER=chromium  # chromium, firefox, webkit
HEADLESS=false
GAJAB_BASE_URL=https://stg.gajab.com

# Appium settings
APPIUM_HOST=127.0.0.1
APPIUM_PORT=4723
APP_PACKAGE=com.example.gajab
APP_ACTIVITY=.MainActivity

# Test data (synthetic values only)
TEST_MOBILE=9999999999
TEST_OTP=TEST_OTP
TEST_PIN=MOCK_PIN

# Timeouts (seconds) — NO hardcoded sleeps
EXPLICIT_WAIT_TIMEOUT=10
PAGE_LOAD_TIMEOUT=15
POLL_INTERVAL=0.5

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
SCREENSHOTS_DIR=./reports/screenshots
```

### Switching Between Web and Mobile

**Option 1: Environment Variable**
```bash
export IS_MOBILE=false  # Web
pytest src/test/python/tests/

export IS_MOBILE=true  # Mobile
pytest src/test/python/tests/
```

**Option 2: CLI Argument**
```bash
pytest src/test/python/tests/ --isMobile  # Mobile
pytest src/test/python/tests/              # Web (default)
```

**Option 3: .env File**
```env
IS_MOBILE=true
```

---

## Logging & Diagnostics

### Log File Format
```
logs/run-20260909-143022.log

2026-09-09 14:30:22 [INFO] [test_login_valid_credentials-12345] [conftest] TEST START: test_login_valid_credentials
2026-09-09 14:30:22 [INFO] [test_login_valid_credentials-12345] [driver_factory] === WEB RUN (Playwright) ===
2026-09-09 14:30:23 [INFO] [test_login_valid_credentials-12345] [base_page_web] Navigating to: https://stg.gajab.com
2026-09-09 14:30:24 [INFO] [test_login_valid_credentials-12345] [login_page_web] Logging in with mobile: [REDACTED]
2026-09-09 14:30:25 [DEBUG] [test_login_valid_credentials-12345] [login_page_web] Clicked: input[placeholder*='Mobile']
...
```

**Key Features**:
- **Timestamp**: When event occurred
- **Level**: DEBUG, INFO, WARN, ERROR
- **Correlation ID**: `[test-name-worker-id]` — uniquely identifies logs from one test
- **Class**: Which module logged the message
- **Message**: Action/result (sensitive data redacted)

### Screenshots & Diagnostics

On test failure:
- Screenshot: `reports/screenshots/test_name-YYYYMMDD-HHMMSS.png`
- Page Source (Web): `reports/diagnostics/test_name-YYYYMMDD-HHMMSS-source.html`
- Logcat (Mobile): `reports/diagnostics/test_name-YYYYMMDD-HHMMSS-logcat.txt`

---

## Parallel Execution

### Running Tests in Parallel (4 workers)

```bash
pip install pytest-xdist
pytest src/test/python/tests/ -v -n 4
```

### CI/CD Matrix

Recommended GitHub Actions workflow:

```yaml
strategy:
  matrix:
    platform: [web, mobile]

env:
  IS_MOBILE: ${{ matrix.platform == 'mobile' && 'true' || 'false' }}

steps:
  - uses: actions/checkout@v3
  - uses: actions/setup-python@v4
    with:
      python-version: '3.9'
  - run: pip install -r requirements.txt
  - run: python -m playwright install
  - run: pytest src/test/python/tests/ -v --html=report.html
```

Both Web and Mobile runs execute in parallel with NO code changes.

---

## Troubleshooting

### Test Hangs/Timeout
- Check `EXPLICIT_WAIT_TIMEOUT` in `.env` (default: 10s)
- Verify element selector is correct in locator-inventory.md
- Check app/browser is responsive (try manual test)

### Element Not Found
- Verify selector in correct format (CSS for Web, XPath or ID for Mobile)
- Check element is visible/displayed (may need scroll first)
- Look at screenshot in `reports/screenshots/` for visual debug

### Appium Connection Failed
- Verify Appium server is running: `appium`
- Check `APPIUM_HOST` and `APPIUM_PORT` in `.env`
- Verify Android emulator/device is connected: `adb devices`

### Playwright Browser Issues
- Re-install browsers: `python -m playwright install`
- Check browser type in `.env`: `BROWSER=chromium|firefox|webkit`

### PII Leaked in Logs
- Verify `StructuredLogger.redact()` pattern covers your data type
- Add new pattern to `REDACT_PATTERNS` if needed
- Never pass raw credentials to tests; use `ConfigLoader.test_*()` methods

---

## SOLID Principles & Architecture Guarantees

| Principle | How Enforced | Benefit |
|-----------|---|---|
| **SRP** | One class = one reason to change (DriverFactory ≠ PageFactory ≠ Logger) | Simple, focused, testable classes |
| **OCP** | Add new page: create interface + 2 impls; no existing code modified | Framework extends without risk |
| **LSP** | Web/Mobile impls fully substitutable behind interface | Single test passes both platforms |
| **ISP** | Small page-specific interfaces, not one giant interface | Tests depend only on methods they use |
| **DIP** | Tests depend on abstractions (interfaces + factories) | `isMobile` resolved in exactly 2 places |

---

## Non-Negotiable Requirements ✓

- [x] **NO hardcoded timeouts** — all waits use config-driven `EXPLICIT_WAIT_TIMEOUT` + `POLL_INTERVAL`
- [x] **isMobile checked in 2 places only** — DriverFactory & PageObjectFactory
- [x] **Reusable wait methods** — waitForVisible, waitForClickable, waitForInvisible, waitForTextPresent, waitForLoadingComplete
- [x] **SOLID + POM** — interfaces + two implementations per workflow
- [x] **Correlation ID logging** — test name + worker ID in every log line
- [x] **Centralized failure hook** — pytest_runtest_makereport captures screenshot/diagnostics once per test
- [x] **Parallel-safe** — pytest fixtures isolate driver per test, no shared mutable state
- [x] **Thread-safe config** — ConfigLoader static methods, read once at session
- [x] **Security** — credentials from env vars (.gitignored), PII redacted in logs
- [x] **Performance** — config-driven poll interval (0.5s), driver cleanup in fixture teardown, duration logged per test

---

## Next Steps

1. **Update locator-inventory.md** with actual Gajab app selectors (Web CSS + Mobile IDs)
2. **Implement remaining workflows** (Product, Bargaining, Checkout, MyBargains) following LoginPage pattern
3. **Set up CI/CD** with GitHub Actions matrix for parallel Web + Mobile runs
4. **Configure test data** in `.env` with real Gajab staging environment details
5. **Run smoke tests** to validate end-to-end pipeline works

---

## Questions?

Refer to:
- [Architecture Design](docs/architecture-design.md) — full design contract
- [Application Map](docs/application-map.md) — app structure
- [Locator Inventory](docs/locator-inventory.md) — all selectors

Good luck with the Automation Quest! 🚀