# Automation Quest Architecture Design — TestAutothon 2026

## High-Level Summary

A unified Web+Mobile framework with:
- **Single test suite** running against both platforms via `isMobile` flag
- **Page Object Model** with interface-based design (one interface per workflow, Web + Mobile implementations)
- **SOLID principles** enforced at every layer
- **No hardcoded waits** — explicit condition-based waits with config-driven timeouts
- **Centralized error handling** — one failure hook captures screenshot + logs + diagnostic dump
- **Structured logging** — every log line tagged with correlation ID (test + worker ID)
- **Parallel-safe** — thread-isolated driver sessions, no shared mutable state
- **Security** — credentials from env vars/git-ignored config, log redaction for PII

---

## Architecture Layers

### Test Layer
- **LoginTest, ProductTest, BargainingTest, CheckoutTest, MyBargainsTest** — business flow tests
- Uses page interfaces only (never Web/Mobile concrete classes)
- Calls `PageObjectFactory.getLoginPage()` to get platform-agnostic `ILoginPage`
- Same test code runs for Web (`isMobile=false`) and Mobile (`isMobile=true`)

### Page Object Interface Layer
- **ILoginPage, IProductPage, IBargainingPage, ICheckoutPage, IMyBargainsPage**
- Small, focused interfaces (ISP) with business methods only
- Tests depend on interfaces only (DIP)

### Web Implementation (Selenium)
- **WebLoginPage, WebProductPage, WebBargainingPage, WebCheckoutPage, WebMyBargainsPage**
- Extend `BasePage` (common Selenium behavior)
- Web-specific locators (CSS/XPath/@testid)
- Implement IXxxPage interfaces

### Mobile Implementation (Appium)
- **MobileLoginScreen, MobileProductScreen, MobileBargainingScreen, MobileCheckoutScreen, MobileMyBargainsScreen**
- Extend `BaseScreen` (common Appium behavior)
- Mobile-specific locators (resourceId/contentDesc)
- Implement IXxxPage interfaces (same interface as Web)

### Factory Layer (Platform Abstraction)
- **ConfigLoader** — reads `isMobile` flag (env var / config file / CLI); centralized config for URLs, timeouts, poll intervals, credentials
- **DriverFactory** — reads `isMobile` flag; creates WebDriver (Selenium) or AppiumDriver (Appium); returns via `IDriverProvider` interface
- **PageObjectFactory** — reads `isMobile` flag; returns Web or Mobile page implementation for each interface

**Critical**: DriverFactory and PageObjectFactory are the ONLY places that check `isMobile` directly. Tests and pages are completely platform-agnostic.

### Utility Layer
- **WaitUtilities** — explicit waits (waitForVisible, waitForClickable, waitForInvisible, waitForTextPresent, waitForLoadingComplete); no hardcoded sleeps
- **ActionUtilities** — safe element interactions (safeClick, safeType, safeGetText, scroll, swipe); exception translation
- **ScreenCapture** — capture screenshots + page source (Web) / logcat (Mobile) on failure
- **StructuredLogger** — per-test logging with correlation ID (test name + worker ID); applies log redaction for credentials/PII

### Exception & Failure Hook
- **CustomExceptions** — ElementNotFoundException, PageLoadTimeoutException, OffersMaxAttemptsExceededException, PaymentGatewayException, etc.
- **FailureHook** — TestNG Listener / JUnit5 Extension / pytest fixture; centralized one-time capture of screenshot + page source + logs on test failure (NOT try/catch per test)

### Security & Configuration
- **SecretsConfig** — load credentials, API keys, test data from environment variables or git-ignored config file (never hardcoded)
- **LogRedaction** — mask credentials, tokens, OTP, mobile numbers, auth headers before logging

### Reporting & CI/CD
- **ReportGenerator** — HTML/JSON reports with execution time, platform flag (isMobile), correlation ID, slow test flagging (>3x median)
- **CI/CD Matrix** — GitHub Actions workflow runs suite twice: `isMobile=false` (Web) and `isMobile=true` (Mobile) in parallel workers

---

## SOLID Mapping

| Principle | Application | Benefit |
|-----------|-------------|---------|
| **SRP** | One class = one reason to change (page ≠ driver ≠ wait ≠ logging) | Classes are simple, testable, maintainable |
| **OCP** | Add new page = create interface + two impls; no existing code modified | Framework extends without ripple effects |
| **LSP** | Web/Mobile impls fully substitutable behind interface; same test passes both | Tests are platform-agnostic; code reuse maximized |
| **ISP** | Small page-specific interfaces, not one giant interface | Tests depend only on methods they use |
| **DIP** | Tests depend on abstractions (interfaces + factories), never concrete classes | `isMobile` flag resolved in exactly two places (DriverFactory, PageObjectFactory) |

---

## Wait/Action Utility Contract

### WaitUtilities
```
waitForVisible(locator, timeoutSeconds) → WebElement
  - Condition: element displayed + enabled
  - Timeout: from config (default 10s)
  - Poll interval: from config (default 500ms)
  - Exception: ElementNotFoundException if timeout

waitForClickable(locator, timeoutSeconds) → WebElement
  - Condition: element visible + enabled + click-ready
  - Exception: ElementNotFoundException

waitForInvisible(locator, timeoutSeconds) → void
  - Condition: element not visible or not present
  - Exception: PageLoadTimeoutException

waitForTextPresent(locator, text, timeoutSeconds) → WebElement
  - Condition: element contains exact or partial text
  - Exception: ElementNotFoundException

waitForLoadingComplete(loadingIndicator, timeoutSeconds) → void
  - Condition: loading spinner absent or invisible
  - Exception: PageLoadTimeoutException (for SPA pages)

All use config-driven timeout + poll interval
All throw custom exceptions (not raw Selenium/Appium exceptions)
All include element + expected condition in exception message
```

### ActionUtilities
```
safeClick(element) → void
  - Action: click with implicit wait for visibility
  - Exception: ElementNotFoundException if click fails

safeType(element, text) → void
  - Action: clear + type with implicit wait
  - Exception: ElementNotFoundException

safeGetText(element) → String
  - Action: get text with implicit wait for visibility
  - Exception: ElementNotFoundException

scroll(element) → void (Web)
  - Action: scroll element into view

swipe(fromX, fromY, toX, toY) → void (Mobile)
  - Action: Appium swipe gesture
  - Exception: Appium-specific exceptions translated to custom

All translate raw driver exceptions into custom exceptions
All include action + element locator in exception context
```

---

## Error Handling Contract

**Centralized Failure Hook** (one hook, one place):
- TestNG Listener / JUnit5 Extension / pytest fixture
- Triggered once per failed test
- Captures:
  - Screenshot: `logs/screenshots/<correlationId>.png`
  - Page source (Web): `logs/diagnostics/<correlationId>-page-source.html`
  - Logcat dump (Mobile): `logs/diagnostics/<correlationId>-logcat.txt`
  - Relevant log excerpt (filtered by correlation ID)
  - Failure stack trace
- Logs via StructuredLogger (includes correlation ID)
- **NOT** try/catch per test method; failures bubble up to hook

---

## Parallel Execution & Cross-Browser Requirements

| Requirement | Implementation |
|-------------|-----------------|
| Driver isolation | ThreadLocal<WebDriver> per test or per-worker fixture |
| No shared mutable state | All dependencies injected; no static fields |
| Cross-browser config | browser=chrome\|firefox\|edge read at suite start per worker |
| isMobile thread-safe | Read once at suite start per worker; immutable thereafter |
| Parallel safe | CI matrix runs `isMobile=false` and `isMobile=true` in separate workers (no shared state) |
| Correlation ID scheme | test name + thread/worker ID → uniquely identifies all logs/screenshots from one test across parallel run |

---

## Logging Requirements

**Format**: `<timestamp> [<level>] [<correlationId>] [<class>] <message>`

**Levels**:
- DEBUG: Every wait attempt, every poll attempt
- INFO: Test start/end, navigation, actions performed
- WARN: Retries, waits exceeding threshold
- ERROR: Failures with stack trace, paths to screenshot/diagnostic

**File**: `logs/run-<yyyyMMdd-HHmmss>.log` per run

**Diagnostic Dump**: `logs/diagnostics/<correlationId>.txt` on failure (page source or logcat + full context)

**Redaction**: Mask patterns like `password.*`, `otp.*`, `mobile.*`, `token.*` before writing

---

## Naming Conventions & Coding Standards

| Category | Pattern | Example |
|----------|---------|---------|
| Interfaces | I<PageName>Page | ILoginPage, IProductPage, IBargainingPage |
| Web Implementations | Web<PageName>Page | WebLoginPage, WebProductPage |
| Mobile Implementations | Mobile<PageName>Screen | MobileLoginScreen, MobileProductScreen |
| Base Classes | Base<Platform> | BasePage, BaseScreen |
| Factories | <Component>Factory | DriverFactory, PageObjectFactory |
| Exceptions | <Noun>Exception | ElementNotFoundException, PageLoadTimeoutException |
| Test Classes | <Feature>Test | LoginTest, BargainingTest, CheckoutTest |
| Methods | verb-first camelCase | loginWithMobile(), submitOTP(), waitForVisible() |
| Test Methods | test_<feature>_<scenario> | test_login_valid_credentials, test_bargaining_three_attempts |

**Header Comments**: Every public method includes "what it does, params, return, exceptions"

---

## Security Requirements

1. **Credentials**: Env vars + git-ignored config file ONLY (no hardcoded secrets in source)
2. **Log Redaction**: Mask credentials/tokens/PII before logging
3. **Test Data**: Synthetic values (9999999999 for mobile, TEST_OTP for OTP, MOCK_PIN for PIN)
4. **No URL Injection**: No raw string concatenation with untrusted input

---

## Performance Requirements

1. **Wait Poll Interval**: Bounded config value (e.g., 500ms), not tight loop
2. **Driver Cleanup**: In finally block or fixture teardown after each test
3. **Duration Capture**: Start/end timestamp logged for every test
4. **Slow Test Flagging**: Tests >3x median duration flagged in report

---

## Platform Selection Contract

| Component | Reads isMobile | Branches on isMobile | Notes |
|-----------|---|---|---|
| ConfigLoader | ✅ YES | N/A | Source of truth for flag |
| DriverFactory | ✅ YES | ✅ YES | Returns Web driver OR Appium driver |
| PageObjectFactory | ✅ YES | ✅ YES | Returns Web page OR Mobile screen |
| BasePage | ❌ NO | ❌ NO | Platform-agnostic, uses driver abstraction |
| BaseScreen | ❌ NO | ❌ NO | Platform-agnostic, uses driver abstraction |
| Tests | ❌ NO | ❌ NO | Platform-agnostic, use only interfaces |
| WaitUtilities | ❌ NO | ❌ NO | Platform-agnostic |
| ActionUtilities | ❌ NO | ❌ NO | Platform-agnostic (except swipe for mobile) |

---

## Gajab-Specific Architectural Patterns

### Multi-Step Authentication (OTP + PIN)
- **Pattern**: Page state machine in ILoginPage implementation
- **Steps**: Mobile Input → OTP Request → OTP Entry → PIN Entry → Success
- **Implementation**: WebLoginPage/MobileLoginScreen tracks current form state
- **Test**: Calls `loginWithMobile()` → `submitOTP()` → `submitPIN()` → `verifyLoginSuccess()` in sequence

### Bargaining Dialog State Machine
- **Pattern**: Modal component with up-to-3 offer cycles
- **States**: OfferSubmitted → CounterReceived → AcceptedOrRejected
- **Implementation**: IBargainingPage.submitOffer() → counter displayed → accept/reject buttons appear
- **Attempt Tracking**: getAttemptCount() returns 1–3; rejectCounter() increments count
- **Test**: Loops up to 3 times: submitOffer() → acceptCounter() or rejectCounter()

### Dynamic Product Lists (Deal/Trending/Just Bargained)
- **Pattern**: Explicit waits for carousel/list JS rendering
- **Tie-Breaking**: IProductPage.selectMostBargainedProduct() implements "first in scroll order" logic
- **Implementation**: waitForLoadingComplete() → iterate through product cards → track index → select first match

### Payment Gateway Redirect (External)
- **Pattern**: Verify redirect URL, don't automate bank login
- **Implementation**: ICheckoutPage.proceedToPayment() returns redirect URL; test verifies URL contains "bank" or "payment"
- **Limitation**: Cannot automate actual bank login (external service); test accepts sandbox mock or captures redirect proof

### My Bargains Authentication
- **Pattern**: Depends on successful login session (not test data generation)
- **Implementation**: IMyBargainsPage requires prior login test to have succeeded; reuses authenticated session
- **Limitation**: Test data is not "clean" (uses real order from prior step); consider test account isolation

---

## Validation Checklist

- [x] Single test suite (not Web/Mobile split)
- [x] Interfaces + two implementations per page (LSP compliance)
- [x] DriverFactory + PageObjectFactory are ONLY places checking isMobile
- [x] No hardcoded timeouts/sleeps (all waits use WaitUtilities)
- [x] Correlation ID + centralized failure hook (not try/catch per test)
- [x] Thread/worker isolation (no shared static mutable state)
- [x] SOLID explicitly mapped to modules
- [x] Mermaid diagram correct + complete

---

## Next Steps (Phase 4)

**Delegate to `aq-tech-stack-selector`** with this architecture as constraint. The tech stack must support:
- Selenium OR Playwright for Web
- Appium UiAutomator2 for Android
- Test runner supporting parameterization by `isMobile` flag (JUnit5, TestNG, pytest)
- Open-source tools only (no paid licenses)
- Single unified framework (not two separate stacks)
