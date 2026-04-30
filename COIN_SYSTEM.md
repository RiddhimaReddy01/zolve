# Zolve Coin System & Testing Guide

Complete documentation of the **two-tier coin system** and how the test suite validates it.

## System Overview

Users have **two types of coins** with different earning sources and use cases:

### 1️⃣ WITHDRAWABLE COINS (Bank-Verified)
**Earned from:** Financial behavior verification
- On-time payment: 500 coins
- Credit score improvement: 400 coins
- Savings milestone: 350 coins
- Direct deposit: 200 coins

**Can be used for:**
- 🏦 **Redeem to Cash** - Convert coins back to dollars via bank transfer
- 🛒 **Z-Kart Purchase** - Spend coins to get 5-10% extra product discount
- 🎁 **Spending Sinks** - Spend on flash deals, clubs, auctions

**Example:**
```
Bank verifies user made on-time credit card payment → 500 withdrawable coins
User can:
  Option A: Redeem $5 (assuming 100:1 ratio) to bank account
  Option B: Spend 250 coins in Z-Kart for $5 savings on $50 product
  Option C: Spend 500 coins on premium auction item
```

### 2️⃣ ECOSYSTEM COINS (Engagement)
**Earned from:** User engagement activities
- Daily check-in: 50 coins
- Ad watch: 10 coins
- Education module: 150 coins
- Referral: 300 coins

**Can be used for:**
- 🛒 **Z-Kart Purchase** - Same 5-10% extra discount as withdrawable
- 🎁 **Spending Sinks** - Flash deals, clubs, auctions
- ❌ **Cannot be redeemed to cash** (ecosystem only)

**Example:**
```
User logs in daily for 7 days → 7 × 50 = 350 ecosystem coins
User can:
  Option A: Spend 250 in Z-Kart to save on shopping
  Option B: Spend 100 in flash deal
  Option C: Join club deal with 350 coins
  ❌ Cannot cash out (ecosystem only)
```

### Total Balance

**Formula:** `Total = Withdrawable + Ecosystem`

**Example:**
```
Withdrawable (from bank): 1000 coins
Ecosystem (from engagement): 500 coins
TOTAL BALANCE: 1500 coins

User can:
- Redeem up to 1000 coins to cash
- Spend all 1500 coins on purchases/sinks
```

## Z-Kart Marketplace (Core Feature)

### How Coin Boost Works

**Standard Purchase:**
```
Product: Starbucks Gift Card
Price: $50
User pays: $50 (card/wallet)
Result: Gets $50 card
```

**Purchase with Coin Boost:**
```
Product: Starbucks Gift Card
Original Price: $50
User has: 250 withdrawable coins

With Coin Boost:
- Extra discount: 10% = $5 savings
- User pays: $50 - $5 = $45 (+ card/wallet payment)
- User spends: 250 coins
- User saves: $5 in actual cash

Result: Gets $50 card, saved $5 cash, spent 250 coins
```

### Products in Z-Kart

**120 Total Products** across categories:

| Category | Brand | Price Range | Discount | Coins |
|----------|-------|-------------|----------|-------|
| Food | Starbucks, Swiggy, Blinkit | $25-$50 | 10% | 150-250 |
| Retail | Amazon, Flipkart, Myntra | $50-$1500 | 5-9% | 250-700 |
| Travel | MakeMyTrip, Uber | $30-$1500 | 6-7% | 150-750 |
| Entertainment | Netflix, Spotify, Cult Fit | $10-$100 | 10-15% | 50-450 |
| Fitness | Decathlon | $100-$2000 | 5% | 500-1000 |

**Decision Logic:**
```
Product Price < $100 → 10-15% discount, lower coins
$100-$500 → 8-10% discount, medium coins
$500+ → 5-9% discount, higher coins (absolute value)
```

## Spending Sinks (Ecosystem Engagement)

Users can spend **both coin types** on engagement activities:

### Flash Deals
- **What:** Time-limited deals on electronics, food, travel
- **Original Price:** $100-$2500
- **Discount:** 25-60% off
- **Coin Cost:** 150-1500 coins
- **Duration:** 15+ minutes (countdown)
- **Coins Type:** Any (withdrawable or ecosystem)

**Example:**
```
Premium Headphones - Flash Deal
Original: $300
Discount: 35% = $105 savings
Final: $195
Coin cost: 500 coins
Users buys: Pay $195 + spend 500 coins → Get headphones
```

### Club Deals
- **What:** Group purchasing to unlock shared benefits
- **Categories:** Housing, Savings, Credit, Travel, Education
- **Min Members:** 5-85 per club
- **Coin Cost:** 200-350 coins/member
- **How it works:**
  1. User joins with coins
  2. Pool grows as members join
  3. Higher pool = better deals
  4. All members benefit

**Example:**
```
Rent Rewards Club
- Each member pays: 250 coins
- Current members: 15
- Pool value: 15 × 250 = 3,750 coins
- Unlock at: 10,000 coins pool
- Benefit: 10% off next 12 months rent
```

### Auctions
- **What:** Premium items with competitive bidding
- **Items:** iPhone, MacBook, flights, staycations, OTT bundles
- **Bid Range:** 450-2200 coins
- **Competitive:** 3-35 bids per item
- **Win:** Highest coin bidder wins

**Example:**
```
iPhone 15 Auction
- Current bid: 1800 coins
- Bids so far: 12
- Time left: 2 hours
- User bids: 2000 coins
- If wins: Gets iPhone, 2000 coins spent
```

### Spin Wheel
- **What:** Gamified reward entries
- **Entry Cost:** 100-500 coins
- **Win Range:** 50-1000 coins
- **RNG:** Each spin is independent

**Example:**
```
Gold Wheel Entry: 250 coins
User spins and lands on: 500 coins reward
Result: Spent 250 coins, won 500 coins = +250 coins net
```

## Bank Integration Testing

### Flow

```
1. USER LINKS BANK ACCOUNT
   └─ Provide: Bank name (HDFC/ICICI/Axis), Account number
   └─ Result: Account linked (simulated OAuth)

2. SYSTEM FETCHES TRANSACTIONS
   └─ Gets: 150 mock transactions with dates, amounts, status
   └─ Detects: On-time/late payments, salary deposits, transfers

3. SYSTEM VERIFIES BEHAVIORS
   └─ Analysis: Payment on-time? Credit score improved? Savings goal met?
   └─ Awards: Coins to withdrawable_balance (can cash out)
   └─ Examples:
      - On-time rent payment ($1000) → 500 coins awarded
      - Credit score improved (+50 points) → 400 coins awarded
      - Salary deposit detected → 200 coins awarded

4. COINS ADDED TO WITHDRAWABLE_BALANCE
   └─ User can: Redeem to cash OR spend in Z-Kart/sinks
   └─ Verified: Bank, not user self-report
```

### Mock Bank Data

**Transaction Types:**
```
Salary/Income: $50,000-$100,000 (on-time) → Verified ✓
Credit Card Payment: $2,000-$5,000 (on-time) → Verified ✓
Rent Payment: $1,000-$2,000 (on-time) → Verified ✓
EMI/Loan Payment: $100-$500 (on-time) → Verified ✓
Utility Bills: $50-$500 (on-time) → Verified ✓
Savings Transfer: $1,000-$10,000 (goal) → Verified ✓
Grocery Spending: $50-$200 (no coins) → Not verified ✗
UPI Transfer: $10-$100 (friends) → Not verified ✗
```

## Test Coverage by Feature

### ✅ Coin Earning (ECOSYSTEM)
```
TEST: test_earn_coins_action
- Action: Daily check-in
- Coins awarded: 50 ecosystem coins
- Frequency: Once per day (anti-spam)
```

### ✅ Bank Verification (WITHDRAWABLE)
```
TEST: test_verify_behaviors
- Input: Linked bank account
- Processing: Analyze 150 transactions
- Output: 500-400-350 coin awards to withdrawable_balance
- Validation: Coins appear in balance, marked as withdrawable
```

### ✅ Balance Management
```
TEST: test_get_balance
- Shows: Total coins breakdown
- Withdrawable: Coins from bank (can redeem or spend)
- Ecosystem: Coins from engagement (can only spend)
- Example output:
  Total: 1450 coins
  Withdrawable: 900 coins (from bank)
  Ecosystem: 550 coins (from engagement)
```

### ✅ Z-Kart Purchase with Coins
```
TEST: test_purchase_with_coin_boost
- Product: Starbucks Gift Card $50
- Coin boost: 10% = $5 extra discount
- Coins cost: 250 withdrawable coins
- Flow:
  1. User sees: Original $50 → With coins: $45 + 250 coins
  2. User purchases: Pays $45, spends 250 coins
  3. System updates: Deducts coins, logs transaction
  4. Result: Total coin balance reduced by 250
- Can use: Withdrawable OR ecosystem coins
```

### ✅ Spending Sinks
```
TEST: test_redeem_flash_deal
- Item: Premium Headphones (was $300, now $195)
- Coin cost: 500 coins
- Flow:
  1. User has: 1000 total coins (600 withdrawable + 400 ecosystem)
  2. User spends: 500 coins (can use either type)
  3. System deducts: 500 from total balance
  4. Result: Balance now 500 coins

TEST: test_join_club_deal
- Club: Rent Rewards (250 coins/member)
- Flow:
  1. User pays: 250 coins (any type)
  2. Pool grows: Total pool now $2500 (10 × 250)
  3. Unlock benefit: When pool hits target
  4. Result: User participated in group purchasing

TEST: test_list_auctions
- Item: iPhone (starting bid 1800 coins)
- Flow:
  1. User places: 2000 coin bid
  2. Coins held: In escrow during auction
  3. Win/Lose: Coins released or charged
```

## Coin Redemption Flow (Theoretical)

**Not currently implemented but architecture supports:**

```
USER REQUESTS: Redeem 500 withdrawable coins to cash

SYSTEM:
1. Validate: User has 500+ withdrawable coins
2. Check: Conversion rate (e.g., 100 coins = $1)
3. Calculate: 500 coins = $5 cash
4. Create: Bank transfer to linked account
5. Record: Transaction in history
6. Update: Deduct from withdrawable_balance
7. Notify: User - "Redeemed 500 coins ($5) to XXX-1234"

RESULT: $5 transferred to user's bank account
```

## Test Validation Matrix

| Feature | Withdrawable | Ecosystem | Z-Kart | Sinks | Redeem |
|---------|--------------|-----------|--------|-------|--------|
| Earn | ✅ Bank verify | ✅ Daily check-in | - | - | - |
| Spend | ✅ Can use | ✅ Can use | ✅ Boost | ✅ Redeem | ✅ To cash |
| Track | ✅ Separate balance | ✅ Separate balance | ✅ Log transaction | ✅ Log transaction | 🏗️ To build |
| Test | test_verify_behaviors | test_earn_coins_action | test_purchase_with_coin_boost | test_redeem_flash_deal | 🏗️ To build |

## Example Complete Journey

```
DAY 1 - Monday
=========
User links HDFC bank account
↓
System fetches 150 transactions
↓
System detects:
  - On-time rent payment: +500 withdrawable coins
  - Credit score +50 points: +400 withdrawable coins
↓
User checks balance:
  Withdrawable: 900 coins (can cash or spend)
  Ecosystem: 0 coins
  Total: 900 coins

User daily check-in:
  +50 ecosystem coins
↓
New balance:
  Withdrawable: 900 coins
  Ecosystem: 50 coins
  Total: 950 coins

---

DAY 2 - Tuesday
=========
User browses Z-Kart products

Starbucks Gift Card: $50
- With 250 coins: 10% off ($5 savings)
- Final: $45 + 250 coins

User purchases:
  1. Pays: $45 to Starbucks
  2. Spends: 250 coins (uses withdrawable coins)
↓
New balance:
  Withdrawable: 650 coins (900 - 250)
  Ecosystem: 50 coins
  Total: 700 coins

User daily check-in:
  +50 ecosystem coins
↓
New balance:
  Withdrawable: 650 coins
  Ecosystem: 100 coins
  Total: 750 coins

---

DAY 3 - Wednesday
=========
User sees Flash Deal: Premium Headphones $195 (was $300)
Coin cost: 500 coins

User redeems:
  1. Spends: 500 coins (uses ecosystem coins first: 100, then withdrawable: 400)
↓
New balance:
  Withdrawable: 250 coins (650 - 400)
  Ecosystem: 0 coins (100 spent)
  Total: 250 coins

At month-end:
User requests: Redeem 250 withdrawable coins to cash
↓
System transfers: $2.50 to user's bank account
(assuming 100 coins = $1 conversion rate)
↓
Final balance:
  Withdrawable: 0 coins (redeemed)
  Ecosystem: 0 coins
  Total: 0 coins
```

## Test Execution Order

```
1. test_verify_behaviors
   └─ Awards: Withdrawable coins from bank
   └─ Result: 900 withdrawable coins earned

2. test_earn_coins_action
   └─ Awards: Ecosystem coins
   └─ Result: 50 ecosystem coins earned

3. test_get_balance
   └─ Shows: 950 total (900 withdrawable + 50 ecosystem)

4. test_purchase_with_coin_boost
   └─ Spends: 250 coins in Z-Kart
   └─ Savings: 5-10% on product
   └─ Result: 700 coins remaining

5. test_redeem_flash_deal
   └─ Spends: 500 coins
   └─ Result: 200 coins remaining

6. test_final_balance_check
   └─ Confirms: Coin totals and types correct
```

## Key Validation Points

✅ **Earning:**
- Bank verified coins go to withdrawable_balance
- Engagement coins go to ecosystem (not withdrawable)
- Daily cap prevents abuse (50 coins/day limit)

✅ **Spending:**
- Both coin types can be spent in Z-Kart and sinks
- Coins deducted correctly from total balance
- Transaction history records accurately

✅ **Z-Kart Boost:**
- 5-10% discount applied correctly
- Coin cost matches product requirement
- Savings calculated as: base_price × discount_pct

✅ **Tier Progression:**
- Calculated based on total coin balance
- Progresses: Basic (0) → Silver (1000) → Gold (3000)

✅ **Withdrawal Path:**
- Withdrawable balance >= total deductions
- Can be converted to cash (future feature)
- Separate from ecosystem coins

## Running Tests

```bash
# Start backend
python backend/main.py

# Run coin system tests
cd tests
python test_user_journeys.py

# Or pytest
pytest test_integration.py -m coins -v
pytest test_integration.py -m marketplace -v
pytest test_integration.py -m sinks -v
```

## Metrics to Monitor

| Metric | Target | Test |
|--------|--------|------|
| Withdrawable earning rate | 500+ coins/behavior | verify_behaviors |
| Daily engagement | 50+ coins/checkin | earn_coins |
| Z-Kart discount | 5-10% savings | purchase_with_boost |
| Coin-to-cash ratio | TBD (e.g., 100:1) | 🏗️ Redemption test |
| Sink engagement | 20%+ of users | redeem_spending_sinks |

---

**For detailed test examples, see `tests/test_user_journeys.py` and `tests/test_integration.py`**
