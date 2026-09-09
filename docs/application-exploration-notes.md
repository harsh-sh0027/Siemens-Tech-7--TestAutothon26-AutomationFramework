# Application Exploration Notes — Gajab Staging

## Summary

**Status**: Phase 1 exploration complete (static analysis). Next phases require interactive browser testing and Android APK inspection.

---

## Key Findings

### Web Application (stg.gajab.com)

1. **Technology**: Next.js SPA (React framework)
   - Implication: Dynamic content rendering → need explicit waits, not `sleep()`
   - Implication: Locators must account for JS rendering delays (10-15s typical)

2. **Authentication Flow**: Multi-step OTP + PIN
   - Step 1: Mobile number entry
   - Step 2: OTP verification (test value: organizer-provided)
   - Step 3: PIN entry (security PIN, test value: organizer-provided)
   - Implication: Must handle 3 sequential form states

3. **Deal of the Day**:
   - Located on home page in a carousel
   - Features 1–2 products daily
   - Implication: Must inspect carousel DOM to extract current product details

4. **Trending Products (🔥)**:
   - Sorted by "most-bargained" metric
   - Tie-breaking rule: **Select first in scroll order**
   - Implication: If multiple products have same bargain count, must iterate through grid in order

5. **Product Listing**:
   - Pagination or infinite scroll (TBD from interactive testing)
   - Price filter: Accepts range (₹427–₹727 for this workflow)
   - Implication: Must verify filter applies correctly

6. **Bargaining Dialog**:
   - Modal overlay (not page navigation)
   - Max 3 offers per product
   - Workflow: Input offer price → Submit → Receive counter → Accept/Reject → Repeat
   - Implication: State machine with 3 maximum iterations

7. **Checkout/Payment**:
   - Order summary displayed
   - Payment methods: Net Banking (primary), Card, UPI
   - Bank selection: "Any Bank" (sandbox for testing)
   - Payment gateway: External redirect (likely bank sandbox or mock)
   - Implication: Cannot automate actual payment; use test/mock credentials

8. **My Bargains**:
   - Post-purchase order history
   - Displays savings/discounts
   - Implication: Requires authenticated session; test data persists across runs

---

### Android Application (APK)

**Status**: Not yet inspected (APK not provided by organizers)

**Expected Structure**:
- Native Android app or React Native
- Same workflows as Web (login → browse → bargain → purchase → My Bargains)
- Platform-specific interactions: back navigation, system dialogs, touch gestures
- Expected locator format: `resourceId` (format: `com.gajab.buyerstore:id/<element_name>`)

**Implication**: Will need adaptive locators in POM (same test, different selectors per platform)

---

## Critical Blockers

| Blocker | Reason | Impact | Workaround |
|---------|--------|--------|-----------|
| OTP/PIN actual delivery | Test requires real SMS or organizer-provided value | Can't validate authentication fully | Use organizer test value (hardcoded) |
| Deal of the Day dynamic | Carousel content unknown until runtime | Must inspect DOM live | Use explicit wait + XPath/selector |
| Bargaining dialog API | Counter-offer logic server-driven | Can't predict offer flow | Record responses, validate state changes |
| Payment gateway external | Bank sandbox or mock redirect | Cannot automate payment itself | Verify redirect URL, mock response if needed |
| Android APK missing | Organizer deliverable not received | Can't inspect Android locators | Wait for APK or use emulator + browser DevTools equiv |

---

## Platform Differences (Web vs. Android)

| Aspect | Web | Android |
|--------|-----|---------|
| **Navigation** | URL/link clicks | Back button, intent navigation |
| **Touch** | Mouse clicks | Single/multi-touch events |
| **Scrolling** | Scroll wheel/momentum | Swipe gestures |
| **Locators** | CSS/XPath/data-testid | resourceId/contentDesc/UiSelector |
| **State Persistence** | URL + sessionStorage | App instance state + SharedPreferences |
| **Dialogs** | Browser modal | Android Dialog/AlertDialog |
| **Payment** | Browser redirect | In-app WebView or external Intent |

---

## Recommended Test Data

### Credentials (Git-Ignored in `config/test-data.json`)

```json
{
  "web": {
    "staging_url": "https://stg.gajab.com/",
    "test_mobile": "9999999999",
    "test_otp": "[ORGANIZER-PROVIDED-VALUE]",
    "test_pin": "[ORGANIZER-PROVIDED-VALUE]"
  },
  "payment": {
    "bank_name": "Any Bank",
    "sandbox_mode": true,
    "account_number": "MOCK_ACCOUNT_123",
    "ifsc": "MOCK0000001"
  },
  "android": {
    "staging_url": "[APK-ENDPOINT-TBD]",
    "app_package": "com.gajab.buyerstore",
    "app_activity": "com.gajab.MainActivity"
  }
}
```

---

## Next Steps

### Immediate (Before Framework Development)
1. [ ] Confirm test OTP and PIN values with organizers
2. [ ] Obtain Android APK file
3. [ ] Set up test environment access (ensure stg.gajab.com is reachable)
4. [ ] Set up Android emulator or device

### During Framework Development
1. [ ] Run Selenium script against stg.gajab.com, inspect each workflow step
2. [ ] Update `docs/locator-inventory.md` with actual locators (replace 🔴 BLOCKED)
3. [ ] Create POM classes with adaptive locators (Web CSS + Android resourceId)
4. [ ] Validate each locator with a quick smoke test

### During Test Execution
1. [ ] Capture screenshots at each critical step (login, product, bargaining, checkout, order)
2. [ ] Verify savings amount in My Bargains
3. [ ] Log actual order ID for audit trail

---

## Known Gotchas

1. **SPA Rendering**: Use `WebDriverWait` (10–15s) before interacting with dynamic elements
2. **Modal Stacking**: OTP form → PIN form → Bargaining modal may appear sequentially; handle state transitions
3. **Price Filter Interaction**: May be range slider (HTML5 `<input type="range">`) or dual input fields; test both
4. **Offer Timing**: Server may delay counter-offer response; use explicit wait with condition
5. **Android Back Button**: May exit bargaining flow; verify navigation state after back press
6. **Payment Redirect**: External gateway may timeout; set explicit timeout (30-60s) and capture redirect URL
7. **Test Data Cleanup**: Multiple test runs may create duplicate orders; ensure test account isolation

---

## References

- **Gajab Staging**: https://stg.gajab.com/
- **Known Category IDs**: Toys & Games (17), Home & Kitchen (1), Electronics (49)
- **Target Product**: Classic 15.7 Inch Soft Tip Dartboard Game Set (ID/slug TBD)
- **Test Credentials**: (Organizer-provided, not included here)
- **Budget**: 15 min exploration (Phase 2) + interactive testing during Phase 5–7

---

## Validation Checklist

- [ ] Web application loads without errors
- [ ] Login page renders and OTP/PIN forms appear after submission
- [ ] Home page sections (Deal, Trending, Just Bargained) are populated
- [ ] Product listing page loads with product cards
- [ ] Price filter UI element is interactive
- [ ] Product detail page renders with name/price/seller info
- [ ] Bargaining button is clickable and opens modal
- [ ] Checkout page displays and payment method selection works
- [ ] My Bargains page requires authentication
- [ ] Android APK available and loadable in emulator
- [ ] All critical locators tested and working
