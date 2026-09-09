# Application Map — Gajab Staging (stg.gajab.com)

## Platform Information
- **Application**: Gajab India's Bargain Bazaar (Staging)
- **Base URL**: https://stg.gajab.com/
- **Technology Stack**: Next.js SPA (React) with dynamic content
- **Authentication**: OTP-based (phone number + PIN)

## Known Pages & Navigation

### 1. HOME PAGE (`/`)
- **Purpose**: Dashboard with featured products and deal sections
- **Key Sections**: Deal of the Day carousel, Trending Products (🔥), Just Bargained, Category navigation
- **Status**: ✅ Accessible (public)

### 2. AUTHENTICATION (`/auth/signin`)
- **Purpose**: Mobile number + OTP + PIN entry
- **State Flow**: Mobile Input → OTP Request → OTP Entry → PIN Entry → Dashboard Redirect
- **Status**: ⚠️ PARTIALLY BLOCKED — Form structure visible but OTP/PIN submission requires live testing

### 3. PRODUCT LISTING (`/product-list/{category}/{id}?offset=0`)
- **Purpose**: Category browse + filter + sort
- **Target Category**: Toys & Games (ID: 17)
- **Known Category IDs**: Home & Kitchen (1), Toys & Games (17), Electronics (49), etc.
- **Status**: ⚠️ BLOCKED — Dynamic product grid, price filter requires interactive testing

### 4. PRODUCT DETAIL PAGE (`/product-detail/{slug}/{product-id}`)
- **Purpose**: Product view + bargaining trigger + cart add
- **Target Product**: Classic 15.7 Inch Soft Tip Dartboard Game Set (ID/slug TBD)
- **Status**: ⚠️ BLOCKED — Dynamic content via JavaScript

### 5. BARGAINING FLOW (Modal Dialog)
- **Purpose**: Multi-step offer negotiation (max 3 attempts)
- **Steps**: Price Input → Submit Offer → Counter Offer Display → Accept/Reject Decision
- **Status**: ⚠️ BLOCKED — Interactive dialog state unknown

### 6. CHECKOUT/PAYMENT (`/checkout?orderId=...`)
- **Purpose**: Order summary + payment method selection + payment gateway redirect
- **Payment Methods**: Net Banking (target), Card, UPI (others)
- **Sandbox Bank**: "Any Bank" test option
- **Status**: 🔴 BLOCKED — External payment gateway

### 7. ORDER CONFIRMATION
- **Purpose**: Order ID display + receipt
- **Status**: 🔴 BLOCKED — Post-payment redirect destination unknown

### 8. MY BARGAINS (`/my-bargains`)
- **Purpose**: Order history + savings display
- **Status**: 🔴 BLOCKED — Requires authentication

---

## Navigation Summary

```
HOME (/) 
├─ → DEAL OF DAY PRODUCT → PRODUCT DETAIL → BARGAINING → CHECKOUT
├─ → TRENDING SECTION → PRODUCT DETAIL → BARGAINING → CHECKOUT  
├─ → JUST BARGAINED SECTION → PRODUCT DETAIL → BARGAINING → CHECKOUT
├─ → CATEGORY MENU → PRODUCT LISTING → FILTER BY PRICE → PRODUCT DETAIL → BARGAINING → CHECKOUT
└─ → LOGIN LINK → AUTH (/auth/signin) → DASHBOARD → MY BARGAINS

PAYMENT FLOW:
CHECKOUT → PAYMENT METHOD SELECT → NET BANKING → BANK SELECT → PAYMENT GATEWAY → CONFIRMATION → MY BARGAINS
```

---

## Critical Blockers for Full Exploration

1. **OTP/PIN Validation** — Requires actual test mobile number and OTP delivery
2. **Dynamic Product Content** — Deal of Day, Trending, Just Bargained products populated by JavaScript
3. **Bargaining Dialog** — Interactive modal with API-driven state transitions
4. **Payment Gateway** — External service (bank redirect) cannot be inspected statically
5. **Android APK** — Organizer-provided file not yet available
6. **My Bargains** — Requires authenticated session

---

## Next Steps

- Use Playwright/Selenium to dynamically inspect elements during test execution
- Capture actual locators via browser DevTools inspection during interactive testing
- Validate Android app structure once APK is provided
- Run a single end-to-end test to map actual UI element IDs
