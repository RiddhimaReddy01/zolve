# Zolve Coin System - Visual Guide

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ZOLVE COIN SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │ WITHDRAWABLE     │        │ ECOSYSTEM        │         │
│  │ COINS            │        │ COINS            │         │
│  ├──────────────────┤        ├──────────────────┤         │
│  │ From: Bank       │        │ From: Engagement │         │
│  │       Verified   │        │       Activities │         │
│  │ • Payment: 500   │        │ • Daily: 50      │         │
│  │ • Credit: 400    │        │ • Ads: 10        │         │
│  │ • Savings: 350   │        │ • Referral: 300  │         │
│  │ • Direct: 200    │        │ • Education: 150 │         │
│  └──────────────────┘        └──────────────────┘         │
│         │                              │                   │
│         │ Can use for:                │ Can use for:      │
│         ├─ Redeem to cash            ├─ Z-Kart          │
│         ├─ Z-Kart discount           ├─ Spending sinks   │
│         └─ Spending sinks            └─ (NO cash out)    │
│                                                             │
│  ┌──────────────────────────────────┐                     │
│  │ TOTAL BALANCE                    │                     │
│  │ Withdrawable + Ecosystem         │                     │
│  │ Determines tier (Basic→Silver→Gold)                    │
│  └──────────────────────────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Coin Sources

```
┌─ BANK VERIFIED (Withdrawable) ──────────────────────┐
│                                                     │
│  Bank Linking                                       │
│  ├─ Link: HDFC / ICICI / Axis                      │
│  ├─ Fetch: 150 mock transactions                   │
│  └─ Verify: Financial behaviors                    │
│                                                     │
│  Behavior Recognition                              │
│  ├─ On-Time Payment         → 500 coins            │
│  ├─ Credit Score +50 pts    → 400 coins            │
│  ├─ Savings Milestone       → 350 coins            │
│  ├─ Direct Deposit Detected → 200 coins            │
│  └─ All → withdrawable_balance (can cash out)      │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─ ENGAGEMENT (Ecosystem) ────────────────────────────┐
│                                                     │
│  Daily Activities                                   │
│  ├─ Check-in (once/day)     → 50 coins             │
│  ├─ Watch Ad               → 10 coins              │
│  ├─ Education Module       → 150 coins             │
│  ├─ Referral              → 300 coins              │
│  └─ All → ecosystem_balance (NO cash out)          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Coin Usage: Z-Kart Purchase

```
WITHOUT COINS:
┌─────────────────────────────────────────────────────┐
│ Starbucks Gift Card: $50                            │
│                                                     │
│ User action: Buy                                    │
│ ┌─────────────────────────────────────────────┐   │
│ │ Pay: $50 (credit card/wallet)               │   │
│ │ Get: $50 Starbucks card                     │   │
│ └─────────────────────────────────────────────┘   │
│ Savings: $0                                         │
└─────────────────────────────────────────────────────┘

WITH COINS (Coin Boost):
┌─────────────────────────────────────────────────────┐
│ Starbucks Gift Card: $50                            │
│ Coin Cost: 250 coins                               │
│ Coin Boost: 10% extra discount = $5 savings        │
│                                                     │
│ User action: Purchase with coins                   │
│ ┌─────────────────────────────────────────────┐   │
│ │ Pay: $50 - $5 = $45 (credit card/wallet)    │   │
│ │ Spend: 250 coins (withdrawable or ecosystem)│   │
│ │ Get: $50 Starbucks card                     │   │
│ └─────────────────────────────────────────────┘   │
│ Savings: $5 in actual cash                         │
│ Cost: 250 coins from balance                       │
│ Net: -$5 price, -250 coins                         │
└─────────────────────────────────────────────────────┘
```

## Coin Usage: Spending Sinks

```
FLASH DEAL:
┌──────────────────────────────────────────┐
│ Premium Headphones - Flash Deal          │
│                                          │
│ Original Price: $300                     │
│ Discount: 35% = $105 off                 │
│ Final Price: $195                        │
│ Coin Cost: 500 coins                     │
│                                          │
│ ┌────────────────────────────────────┐  │
│ │ User buys:                         │  │
│ │ • Spends: 500 coins (any type)    │  │
│ │ • Pays: $195 to merchant           │  │
│ │ • Gets: Headphones                 │  │
│ │ • Total saved: $105 (from deal)    │  │
│ └────────────────────────────────────┘  │
│ Coins usage: 500 deducted from balance   │
└──────────────────────────────────────────┘

CLUB DEAL:
┌──────────────────────────────────────────┐
│ Rent Rewards Club                        │
│                                          │
│ Coin Cost per Member: 250 coins          │
│ Current Members: 15                      │
│ Pool Value: 15 × 250 = 3,750 coins      │
│                                          │
│ ┌────────────────────────────────────┐  │
│ │ User joins:                        │  │
│ │ • Spends: 250 coins (any type)    │  │
│ │ • Joins pool: Now 16 members       │  │
│ │ • New pool: 4,000 coins            │  │
│ │ • Benefit: When pool hits 10k      │  │
│ │           Get 10% off rent (12mo)  │  │
│ └────────────────────────────────────┘  │
│ Coins usage: 250 deducted from balance   │
└──────────────────────────────────────────┘

AUCTION:
┌──────────────────────────────────────────┐
│ iPhone 15 Auction                        │
│                                          │
│ Starting Bid: 1,000 coins                │
│ Current Bid: 1,800 coins (12 bids)       │
│ Time Left: 2 hours                       │
│                                          │
│ ┌────────────────────────────────────┐  │
│ │ User bids:                         │  │
│ │ • Bids: 2,000 coins (any type)    │  │
│ │ • Status: Now winning bid          │  │
│ │ • Coins held: In escrow            │  │
│ │ • Win: Gets iPhone, coins charged  │  │
│ │ • Lose: Coins released             │  │
│ └────────────────────────────────────┘  │
│ Coins usage: 2,000 if wins, 0 if loses   │
└──────────────────────────────────────────┘
```

## Coin Redemption Path

```
┌─────────────────────────────────────────────────────┐
│ COIN REDEMPTION (Withdrawable Only)                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Step 1: User has Withdrawable Coins                │
│ ┌─────────────────────────────────────────────┐   │
│ │ User balance:                               │   │
│ │ • Withdrawable: 900 coins                   │   │
│ │ • Ecosystem: 100 coins                      │   │
│ │ • Total: 1,000 coins                        │   │
│ └─────────────────────────────────────────────┘   │
│                          ↓                          │
│ Step 2: User requests Redemption                   │
│ ┌─────────────────────────────────────────────┐   │
│ │ "Redeem 500 withdrawable coins to cash"     │   │
│ └─────────────────────────────────────────────┘   │
│                          ↓                          │
│ Step 3: System validates & converts               │
│ ┌─────────────────────────────────────────────┐   │
│ │ Validation:                                 │   │
│ │ ✓ Has 900 withdrawable (need 500)           │   │
│ │ Conversion:                                 │   │
│ │ • Rate: 100 coins = $1                      │   │
│ │ • 500 coins = $5                            │   │
│ └─────────────────────────────────────────────┘   │
│                          ↓                          │
│ Step 4: System initiates bank transfer             │
│ ┌─────────────────────────────────────────────┐   │
│ │ Bank Transfer:                              │   │
│ │ • To: HDFC account ending in -1234          │   │
│ │ • Amount: $5                                │   │
│ │ • Status: Pending (2-3 business days)       │   │
│ └─────────────────────────────────────────────┘   │
│                          ↓                          │
│ Step 5: Update balance & notify                    │
│ ┌─────────────────────────────────────────────┐   │
│ │ New balance:                                │   │
│ │ • Withdrawable: 400 coins (900 - 500)      │   │
│ │ • Ecosystem: 100 coins                      │   │
│ │ • Total: 500 coins                          │   │
│ │                                             │   │
│ │ Notification:                               │   │
│ │ "✓ Redeemed 500 coins ($5) to -1234"       │   │
│ │ "Available in 2-3 business days"            │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘

NOTE: Ecosystem coins CANNOT be redeemed to cash
Only withdrawable coins (from bank verification) can be cashed out
```

## Complete User Journey

```
DAY 1: Bank Verification
┌─────────────────────────────────────────────────────┐
│ 1. User links HDFC account                          │
│ 2. System fetches 150 transactions                  │
│ 3. System analyzes behaviors:                       │
│    • Last 3 rent payments on-time → +500 coins     │
│    • Credit score improved +50 pts → +400 coins    │
│ 4. NEW BALANCE:                                     │
│    Withdrawable: 900 | Ecosystem: 0 | Total: 900   │
└─────────────────────────────────────────────────────┘

DAY 2: Z-Kart Purchase
┌─────────────────────────────────────────────────────┐
│ 1. User browses Z-Kart                              │
│ 2. Finds Starbucks card: $50                        │
│    • With 250 coins: 10% off ($5 savings)           │
│ 3. User purchases with coins                        │
│ 4. Transaction:                                     │
│    • Coins spent: 250 (from withdrawable)           │
│    • Price paid: $45 (instead of $50)               │
│    • Gets: $50 Starbucks card                       │
│ 5. NEW BALANCE:                                     │
│    Withdrawable: 650 | Ecosystem: 0 | Total: 650   │
│ 6. User saved: $5 in actual cash by spending coins │
└─────────────────────────────────────────────────────┘

DAY 3: Engagement Activity
┌─────────────────────────────────────────────────────┐
│ 1. User does daily check-in                         │
│ 2. System awards: +50 ecosystem coins               │
│ 3. NEW BALANCE:                                     │
│    Withdrawable: 650 | Ecosystem: 50 | Total: 700  │
└─────────────────────────────────────────────────────┘

DAY 4: Spending Sink
┌─────────────────────────────────────────────────────┐
│ 1. User sees flash deal: Premium headphones $195    │
│    (was $300, costs 500 coins)                      │
│ 2. User redeems:                                    │
│    • Spends 500 coins (uses ecosystem first 50,    │
│      then withdrawable 450)                         │
│    • Pays $195 to merchant                          │
│ 3. NEW BALANCE:                                     │
│    Withdrawable: 200 | Ecosystem: 0 | Total: 200   │
└─────────────────────────────────────────────────────┘

DAY 5+: Earn More & Build Up
┌─────────────────────────────────────────────────────┐
│ • Daily check-ins: +50 coins each (ecosystem)       │
│ • Ads watched: +10 coins (ecosystem)                │
│ • After 10 days of check-ins: +500 ecosystem coins  │
│ • New balance: 200 withdrawable + 500 ecosystem     │
│ • Total: 700 coins → Can reach Silver tier (1000)   │
└─────────────────────────────────────────────────────┘

END: Coin Redemption
┌─────────────────────────────────────────────────────┐
│ 1. User reaches 1,000 total coins (Silver tier)     │
│    Breakdown: 300 withdrawable + 700 ecosystem      │
│ 2. User requests: Redeem 300 withdrawable to cash   │
│ 3. System transfers: $3 to HDFC account (100:1)     │
│ 4. FINAL BALANCE:                                   │
│    Withdrawable: 0 | Ecosystem: 700 | Total: 700    │
│    Ecosystem coins remain (can spend more)          │
│ 5. User notification:                               │
│    "✓ Redeemed $3 to HDFC -1234 (2-3 days)"        │
└─────────────────────────────────────────────────────┘
```

## Test Coverage Map

```
┌─────────────────────────────────────────────────────┐
│         TEST SUITE FEATURE COVERAGE                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ BANK INTEGRATION                                    │
│ ├─ test_link_bank_account                 ✅        │
│ ├─ test_get_bank_transactions              ✅        │
│ ├─ test_verify_behaviors                   ✅        │
│ └─ test_get_credit_score                   ✅        │
│                                                     │
│ COIN EARNING (ECOSYSTEM)                           │
│ ├─ test_earn_coins_action                  ✅        │
│ └─ test_get_coin_history                   ✅        │
│                                                     │
│ COIN EARNING (WITHDRAWABLE)                        │
│ ├─ test_verify_behaviors                   ✅        │
│ └─ Result: withdrawable_balance increased ✅        │
│                                                     │
│ BALANCE MANAGEMENT                                  │
│ ├─ test_get_balance                        ✅        │
│ │  └─ Shows: Withdrawable vs Ecosystem     ✅        │
│ └─ test_get_user_dashboard                 ✅        │
│                                                     │
│ Z-KART PURCHASE (WITH COIN BOOST)          ✅✅✅   │
│ ├─ test_list_zmart_products                ✅        │
│ ├─ test_get_product_details                ✅        │
│ └─ test_purchase_with_coin_boost           ✅ MAIN  │
│    └─ Validates: Coin deduction + Savings ✅        │
│                                                     │
│ SPENDING SINKS                                      │
│ ├─ test_list_flash_deals                   ✅        │
│ ├─ test_list_club_deals                    ✅        │
│ ├─ test_list_auctions                      ✅        │
│ ├─ test_redeem_flash_deal                  ✅        │
│ └─ test_join_club_deal                     ✅        │
│                                                     │
│ COIN REDEMPTION TO CASH (Future)                    │
│ ├─ test_redeem_to_cash                     🏗️        │
│ └─ Validates: withdrawable → $              🏗️        │
│                                                     │
└─────────────────────────────────────────────────────┘

Legend:
✅  = Implemented & tested
🏗️  = Architecture ready, not yet implemented
```

## Key Numbers Reference

```
EARNING RATES:
  Bank-verified:
    - On-time payment: 500 withdrawable coins
    - Credit score +50: 400 withdrawable coins
    - Savings milestone: 350 withdrawable coins
    - Direct deposit: 200 withdrawable coins
  
  Engagement:
    - Daily check-in: 50 ecosystem coins
    - Ad watch: 10 ecosystem coins
    - Education: 150 ecosystem coins
    - Referral: 300 ecosystem coins

Z-KART PRICING:
  - Products: 120 total
  - Price range: $25-$2,000
  - Coin discount: 5-15%
  - Coins per product: 150-1,000

SPENDING SINKS:
  - Flash deals: 150-1,500 coins
  - Club deals: 200-350 coins
  - Auctions: 450-2,200 coins
  - Spin wheel: 100-500 coins

TIERS:
  - Basic: 0-999 coins
  - Silver: 1,000-2,999 coins
  - Gold: 3,000+ coins

REDEMPTION (Proposed):
  - Rate: 100 coins = $1
  - Min: 50 coins
  - Max: Withdrawable balance
```

---

**For implementation details, see `COIN_SYSTEM.md`**  
**For test code, see `tests/test_user_journeys.py`**
