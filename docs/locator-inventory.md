# Locator Inventory — Gajab Web & Android

## Discovery Status: PHASE 1 (Static Analysis Complete, Interactive Testing Pending)

This inventory will be updated as each locator is discovered and validated during test execution.

---

## WEB PLATFORM (Next.js SPA at stg.gajab.com)

### HIGH-CONFIDENCE LOCATORS (Verified or Semantic)

| Element | Location | Locator Type | Locator Value | Stability | Notes |
|---------|----------|--------------|---------------|-----------|-------|
| Login/Sign-up Link | Header (top-right) | Link text | `Log in / Sign up` or `href="/auth/signin"` | ✅ STABLE | Public, always visible |
| Logo | Header (top-left) | Image alt or href | `href="/"` or `img[alt*="Gajab"]` | ✅ STABLE | Home link |
| Search Icon | Header (center) | Button role | `role="button"` + `aria-label="search"` (assumed) | ⚠️ NEEDS VERIFY | Standard pattern |
| Navigation Menu | Header | Nav role | `role="navigation"` or `<nav>` | ⚠️ NEEDS VERIFY | Contains category links |

### MEDIUM-CONFIDENCE LOCATORS (Assumed Patterns)

| Element | Location | Locator Type | Expected Pattern | Fallback | Status |
|---------|----------|--------------|------------------|----------|--------|
| Mobile Input (Login) | `/auth/signin` form | `data-testid` (assumed) | `data-testid="mobile-input"` | `input[placeholder*="Mobile"]` | 🔴 BLOCKED |
| Request OTP Button | `/auth/signin` form | Button text or `data-testid` | `text="Request OTP"` or `data-testid="request-otp"` | `button[type="submit"]` | 🔴 BLOCKED |
| OTP Input Field | `/auth/signin` form (post-submit) | `data-testid` (assumed) | `data-testid="otp-input"` | `input[maxlength="6"]` | 🔴 BLOCKED |
| PIN Input Field | `/auth/signin` form (post-OTP) | `data-testid` (assumed) | `data-testid="pin-input"` | `input[type="password"]` | 🔴 BLOCKED |
| T&C Checkbox | `/auth/signin` form | Checkbox role | `role="checkbox"` + text | `input[type="checkbox"]` | 🔴 BLOCKED |

### DYNAMIC CONTENT (JS-Rendered, Requires Interactive Testing)

| Section | Element | Expected Locator Pattern | Status |
|---------|---------|-------------------------|--------|
| Deal of the Day | Carousel container | `data-testid="deal-carousel"` or `.carousel` | 🔴 BLOCKED |
| Deal of the Day | Previous/Next arrows | `data-testid="carousel-prev"`, `"carousel-next"` or `img[alt*="arrow"]` | 🔴 BLOCKED |
| Deal of the Day | Product card link | `href="/product-detail/..."` within carousel | 🔴 BLOCKED |
| Trending (🔥) | Section header | Text: "Trending" or `data-testid="trending-section"` | 🔴 BLOCKED |
| Trending | Product cards | `data-testid="product-card"` or `article` or `.product-grid-item` | 🔴 BLOCKED |
| Trending | "View All" link | Text: "View All" or `href="/product-list/all?widgetId=11"` | ⚠️ NEEDS VERIFY |
| Just Bargained | "View All" link | Text: "View All" or `href="/product-list/all?widgetId=10"` | ⚠️ NEEDS VERIFY |
| Just Bargained | Product cards | `data-testid="product-card"` or `.product-grid-item` | 🔴 BLOCKED |

### CATEGORY NAVIGATION

| Category | URL Pattern | Category ID | Status |
|----------|------------|-------------|--------|
| Toys & Games | `/product-list/toys-games/17` | `17` | ⚠️ NEEDS VERIFY |
| Home & Kitchen | `/product-list/home-kitchen/1` | `1` | ⚠️ NEEDS VERIFY |
| Electronics | `/product-list/electronics/49` | `49` | ⚠️ NEEDS VERIFY |

**To navigate:** Click nav link with text matching category name, or direct URL with known ID.

### PRODUCT LISTING PAGE (`/product-list/toys-games/17`)

| Element | Expected Pattern | Status |
|---------|-----------------|--------|
| Price Filter Range | `input[type="range"]` or min/max inputs with `data-testid="price-filter"` | 🔴 BLOCKED |
| Sort/Filter Dropdown | `select` or button with `aria-label="Sort"` | 🔴 BLOCKED |
| Product Grid | `data-testid="product-grid"` or `.products-container` or `section[role="region"]` | 🔴 BLOCKED |
| Product Cards | `data-testid="product-card"` or `article` | 🔴 BLOCKED |
| Pagination/Scroll | Infinite scroll or `button[aria-label="Load more"]` | 🔴 BLOCKED |

### PRODUCT DETAIL PAGE (`/product-detail/{slug}/{productId}`)

| Element | Expected Pattern | Status |
|---------|-----------------|--------|
| Product Title | `h1` or `data-testid="product-title"` | 🔴 BLOCKED |
| Product Image | `img[src*="product"]` or `data-testid="product-image"` | 🔴 BLOCKED |
| Original Price | `data-testid="original-price"` or `.price-original` (strikethrough) | 🔴 BLOCKED |
| Asking Price | `data-testid="asking-price"` or `.price-asking` (bold/highlighted) | 🔴 BLOCKED |
| Seller Name | `data-testid="seller-name"` or `.seller-info` | 🔴 BLOCKED |
| Seller City | `data-testid="seller-city"` or `.seller-location` | 🔴 BLOCKED |
| "Start Bargaining" Button | `button[text="Start Bargaining"]` or `data-testid="bargain-btn"` | 🔴 BLOCKED |
| "Add to Cart" Button | `button[text="Add to Cart"]` or `data-testid="add-cart-btn"` | 🔴 BLOCKED |

### BARGAINING DIALOG (Modal)

| Element | Expected Pattern | Status |
|---------|-----------------|--------|
| Modal Container | `role="dialog"` or `.modal` or `data-testid="bargain-modal"` | 🔴 BLOCKED |
| Price Input | `input[type="number"]` with `aria-label="Offer Price"` or `data-testid="offer-price"` | 🔴 BLOCKED |
| "Submit Offer" Button | `button[text="Submit"]` or `data-testid="submit-offer-btn"` | 🔴 BLOCKED |
| Counter Offer Display | `data-testid="counter-offer"` or `.counter-offer-box` | 🔴 BLOCKED |
| "Accept" Button | `button[text="Accept"]` or `data-testid="accept-offer-btn"` | 🔴 BLOCKED |
| "Reject" Button | `button[text="Reject"]` or `data-testid="reject-offer-btn"` | 🔴 BLOCKED |
| Attempt Counter | Text: "Attempt X of 3" or `data-testid="attempt-counter"` | 🔴 BLOCKED |

### CHECKOUT/PAYMENT FLOW

| Element | Expected Pattern | Status |
|---------|-----------------|--------|
| Order Summary | `data-testid="order-summary"` or `.order-summary-box` | 🔴 BLOCKED |
| Payment Method Options | `radio` buttons or `select` with Net Banking / Card / UPI | 🔴 BLOCKED |
| "Net Banking" Radio | `input[value="netbanking"]` or label text: "Net Banking" | 🔴 BLOCKED |
| Bank Select Dropdown | `select[aria-label="Select Bank"]` or `data-testid="bank-select"` | 🔴 BLOCKED |
| "Proceed to Payment" Button | `button[text="Pay Now"]` or `data-testid="proceed-payment-btn"` | 🔴 BLOCKED |

### MY BARGAINS PAGE (`/my-bargains`)

| Element | Expected Pattern | Status |
|---------|-----------------|--------|
| Total Savings Display | `data-testid="total-savings"` or `.savings-amount` with rupee symbol | 🔴 BLOCKED (Auth Required) |
| Orders List | `ul[role="list"]` or `.orders-container` | 🔴 BLOCKED (Auth Required) |
| Order Item Card | `li[role="listitem"]` or `.order-card` | 🔴 BLOCKED (Auth Required) |
| Discount per Order | `data-testid="discount-amount"` or `.discount-label` | 🔴 BLOCKED (Auth Required) |

---

## ANDROID PLATFORM (APK)

### Status: 🔴 NOT YET AVAILABLE
**Reason**: Organizer-provided Android APK file not yet received.

### Expected Locator Strategy for Android

| Component | Expected Resource ID Pattern | Alternative Locator | Status |
|-----------|------------------------------|-------------------|--------|
| Mobile Input | `com.gajab.buyerstore:id/mobile_input` (guess) | Text input in login activity | 🔴 PENDING APK |
| OTP Input | `com.gajab.buyerstore:id/otp_input` (guess) | 6-digit numeric input | 🔴 PENDING APK |
| PIN Input | `com.gajab.buyerstore:id/pin_input` (guess) | Numeric input (hidden chars) | 🔴 PENDING APK |
| Start Bargaining Button | `com.gajab.buyerstore:id/bargain_btn` (guess) | Button element (UiAutomator2: `new UiSelector().text("Start Bargaining")`) | 🔴 PENDING APK |
| Offer Price Input | `com.gajab.buyerstore:id/offer_price_input` (guess) | EditText in dialog | 🔴 PENDING APK |
| Submit Offer Button | `com.gajab.buyerstore:id/submit_offer_btn` (guess) | Button text: "Submit" or "Make Offer" | 🔴 PENDING APK |
| Accept Offer Button | `com.gajab.buyerstore:id/accept_btn` (guess) | Button text: "Accept" | 🔴 PENDING APK |

### How to Inspect Android APK

Once provided:
```bash
# 1. Decompile APK
apktool d Gajab.apk

# 2. View resource IDs in manifest + layout files
# Location: Gajab/res/layout/*.xml

# 3. Use Appium Inspector (easiest for active testing)
# Run emulator → Open APK → Launch Appium Inspector
# Inspector displays element hierarchy with resourceId + contentDesc

# 4. Use Android Studio Layout Inspector
# Run app in emulator → Tools → Layout Inspector
# Shows live UI tree with element properties
```

---

## DISCOVERY PLAN

### Phase 1 (Current): Static Analysis ✅ COMPLETE
- Identified page structure from web exploration
- Documented known URLs and navigation patterns
- Created locator templates

### Phase 2 (Pending): Interactive Web Testing
- [ ] Open stg.gajab.com in browser with DevTools
- [ ] Navigate each workflow step (login → product → bargaining → checkout)
- [ ] Inspect elements live to get exact `data-testid`, `aria-label`, class names
- [ ] Update this inventory with ACTUAL locators (replace 🔴 BLOCKED with ✅ VERIFIED)
- [ ] Test each locator in a Selenium/Playwright script
- [ ] Validate assertions (visibility, clickability, value extraction)

### Phase 3 (Pending): Android Inspection
- [ ] Receive organizer Android APK
- [ ] Load into emulator
- [ ] Use Appium Inspector to discover resource IDs
- [ ] Compare UI patterns with Web version (same elements, different locators)
- [ ] Update Android section with actual `resourceId` values

### Phase 4 (Pending): Cross-Platform Locator Mapping
- [ ] Create a locator translation table (Web `data-testid` → Android `resourceId`)
- [ ] Validate adaptive locator strategy in POM (same method, platform-specific selector)

---

## Validation Checklist

- [ ] Deal of the Day carousel loads and contains clickable product links
- [ ] Trending section displays products with working links
- [ ] Just Bargained section displays products with working links
- [ ] Category navigation (Toys & Games) loads product listing
- [ ] Price filter (₹427–₹727) works and filters results correctly
- [ ] Product detail page loads for Dartboard Game Set
- [ ] Bargaining dialog opens, accepts 3 offers, can accept one
- [ ] Checkout displays order summary and payment methods
- [ ] Net Banking payment flow initiates (redirect or sandbox mock)
- [ ] Order confirmation shows order ID
- [ ] My Bargains displays savings information
- [ ] Android APK screens match Web navigation patterns
- [ ] All locators tested and passing (no stale element exceptions)

---

## Notes

- All Web locators assume Next.js SPA with React-rendered content
- Price filter and dynamic content require explicit waits (Selenium `WebDriverWait` or Playwright `waitForSelector`)
- Payment gateway is external; test may redirect to actual bank sandbox or mock page
- Android APK expected to be native app or React Native; locator strategy may differ
- Sensitive values (test OTP, bank credentials) will be externalized to `config/test-data.json` (git-ignored)
