# Zolve Z-Coins System Design — 5-Hour Hackathon MVP

## 1. Executive Summary

Build a **full-featured demo** of the Zolve behavioral finance platform in 5 hours showing **breadth over depth**:

> Ecosystem: Earning → Commerce → Gamification → Social → Intelligence

**Tech Stack:**
- Frontend: Streamlit + CRED-inspired CSS (dark, glassmorphic)
- Backend: FastAPI + SQLite
- Architecture: Single-user demo, client-server MVP

**Scope Strategy:** Show ALL features from spec. Some are fully functional (earnings, tier, marketplace), some are simulated/UI-only (auctions, referrals, price compare). This is a **showcase/prototype**, not production-grade.

---

## 2. System Architecture

### 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                      │
│         (Dashboard | Earn | Z-Kart | Play)              │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP REST (requests library)
                   ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  (7 endpoints: health, user, action, zkart, purchase,   │
│   scratch, leaderboard)                                 │
└──────────────────┬──────────────────────────────────────┘
                   │ sqlite3 (raw SQL)
                   ↓
┌─────────────────────────────────────────────────────────┐
│               SQLite Database                            │
│  (users, coin_transactions, products, purchases,        │
│   behaviors)                                            │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Port & Service Layout

| Service | Port | Purpose |
|---------|------|---------|
| FastAPI | 8000 | Backend API, handles earning/spending/core logic + simulated features |
| Streamlit | 8501 | Frontend UI, 9 pages showing full ecosystem |
| SQLite | (file-based) | `zolve.db` in project root |

**No external services. Everything local. Some features (auctions, referrals) use simulated data for demo purposes.**

---

## 3. Data Model

### 3.1 Database Schema

```sql
-- Users (one demo user to start)
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  coin_balance INTEGER DEFAULT 0,
  tier TEXT DEFAULT 'Basic',  -- Basic | Silver | Gold
  credit_score INTEGER DEFAULT 650,
  bank_linked BOOLEAN DEFAULT 0,  -- has user linked account?
  linked_bank_name TEXT,  -- 'HDFC', 'ICICI', 'Axis', etc.
  last_behavior_check TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Coin transaction log (full audit trail)
CREATE TABLE coin_transactions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  amount INTEGER NOT NULL,  -- positive = earn, negative = spend
  event_type TEXT NOT NULL,  -- 'payment', 'savings', 'scratch', 'purchase', etc.
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- CRITICAL: Verified financial behaviors (behavioral tracking)
CREATE TABLE behaviors (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  behavior_type TEXT NOT NULL,  -- 'on_time_payment', 'credit_score_up', 'savings_milestone'
  verified BOOLEAN DEFAULT 0,  -- was this verified by bank/app?
  verification_source TEXT,  -- 'bank_api', 'user_claim', 'system_detected'
  behavior_data TEXT,  -- JSON: {"payment_date": "2024-01-15", "amount": 5000, "status": "on_time"}
  completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bank account linking & transaction history
CREATE TABLE linked_accounts (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  bank_name TEXT NOT NULL,  -- 'HDFC', 'ICICI', 'Axis', etc.
  account_type TEXT,  -- 'checking', 'savings', 'credit_card'
  masked_account_number TEXT,  -- for display: '****5678'
  linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_sync TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Bank transaction cache (from mock API)
CREATE TABLE bank_transactions (
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL,
  transaction_date DATE,
  description TEXT,
  amount REAL,
  transaction_type TEXT,  -- 'debit', 'credit', 'payment'
  status TEXT,  -- 'completed', 'pending'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES linked_accounts(id)
);

-- Credit score history (from mock bureau)
CREATE TABLE credit_score_history (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  score INTEGER,
  score_date DATE,
  bureau TEXT,  -- 'Experian', 'CIBIL', 'Equifax'
  fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Savings goals tracking
CREATE TABLE savings_goals (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  goal_name TEXT,  -- 'Emergency Fund', 'Vacation', etc.
  target_amount REAL,
  current_amount REAL,
  target_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Z-Kart products
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,  -- 'food', 'travel', 'retail', 'entertainment'
  base_price REAL NOT NULL,
  coin_discount_pct INTEGER DEFAULT 10,  -- additional % off with coins
  coins_required INTEGER NOT NULL,  -- min coins to unlock discount
  stock INTEGER DEFAULT 100
);

-- Purchase history
CREATE TABLE purchases (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  coins_spent INTEGER NOT NULL,
  purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### 3.2 Seed Data

**Demo User:**
```json
{
  "id": 1,
  "name": "Alex",
  "email": "demo@zolve.app",
  "coin_balance": 0,
  "tier": "Basic",
  "credit_score": 650
}
```

**Products (8 items, 2 per category):**
- Food: "Coffee Voucher" ($5), "Dinner Discount" ($50)
- Travel: "Flight Credit" ($200), "Hotel Night" ($150)
- Retail: "Fashion Coupon" ($100), "Tech Accessory" ($75)
- Entertainment: "Movie Pass" ($20), "Gaming Credit" ($60)

---

## 4. Business Logic: Z-Coins Engine

### 4.0 NEW: Behavior Verification & Tracking

**The Key Insight:** Zolve doesn't just reward actions—it VERIFIES them.

**3 Verification Methods:**

#### Method 1: Mock Bank API (Primary) ✅
When user links bank account, we call simulated bank API:
```
POST /api/bank/verify-transactions
→ Returns simulated transaction data
→ Detects: "Payment on 2024-01-15, amount ₹5000, status: ON_TIME"
→ Awards 500 coins
→ Logs to behaviors table with verification_source='bank_api'
```

**Mock Banks (for demo):**
- HDFC Bank (returns mock credit card transactions)
- ICICI Bank (returns mock savings account)
- Axis Bank (returns mock checking account)

#### Method 2: User Self-Report (Secondary)
User submits evidence for review, but coins are not awarded until a mock verifier confirms the behavior:
- "I paid my credit card on time" → form submission
- System validates via mock bank or credit bureau data
- If verified → coins awarded
- If unverified → no coins, status shows "verification required"

#### Method 3: System Auto-Detection
- Daily check-in streak → triggers bonus
- Savings goal milestones → auto-detected
- Easter eggs → hidden triggers detected

### 4.1 Earning Mechanism (NOW WITH VERIFICATION)

**Earning Weights (from spec, all 9 event types):**

| Event | Coins | Category | Verification | Status |
|-------|-------|----------|--------------|--------|
| On-time Payment | 500 | Financial Discipline | Bank API | ✅ Functional |
| Credit Score ↑ | 400 | Credit Improvement | Mock Bureau API | ✅ Functional |
| Savings Milestone | 350 | Savings Behavior | Goal tracking | ✅ Functional |
| Direct Deposit | 200 | Banking Setup | Bank API | ✅ Functional |
| Education Module | 150 | Learning | User self-report | ✅ Functional |
| Daily Check-in | 50 | Engagement | System auto | ✅ Functional |
| Ad Watch | 10 | Monetization | System auto | ✅ Functional |
| Referral | 300 | Growth | Link tracking | 🎭 Simulated |
| Easter Egg | 200-1000 | Hidden | Trigger detection | 🎭 Simulated |

**Implementation: `game_engine.py`**
- Function `calculate_coins(event_type: str) -> int` returns coin amount
- Daily cap enforcement via `check_daily_cap(user_id, event_type) -> bool`
- All coin changes logged to `coin_transactions` table

### 4.2 Tier System

**Logic:** Tier determined by (1) coin balance + (2) number of completed unique behaviors

| Tier | Coin Range | Behavior Requirement | Unlock |
|------|-----------|----------------------|--------|
| Basic | 0–999 | — | Entry |
| Silver | 1000–2999 | 2+ unique behaviors | Multipliers, flash deals |
| Gold | 3000+ | 5+ unique behaviors | Auction access, ad-free |

**Real-time recalculation:** Every coin transaction triggers `calculate_tier(user_id)`.

### 4.3 Spending Mechanisms

**All Spending Sinks (from spec):**

| Sink | Coins Cost | Type | Status |
|------|-----------|------|--------|
| Z-Kart Discount | 50-300 | Direct purchase | ✅ Functional |
| Spin Wheel Entry | 100 | Game entry | ✅ Functional |
| Scratch Card Entry | Free | Game entry | ✅ Functional (no cost) |
| Flash Deal | 200-500 | Limited-time offer | 🎭 Simulated UI |
| Auction Bid | Variable | Competitive | 🎭 Simulated UI |
| Club Deal | 100-400 | Group purchase | 🎭 Simulated (shows product) |

**Z-Kart Purchase (Fully Functional):**
1. User selects product in marketplace
2. `POST /api/purchase` called with product_id
3. Backend checks: user has enough coins, product in stock
4. Deduct coins: `coin_balance -= coins_required`
5. Log negative transaction to `coin_transactions`
6. Record in `purchases` table for history
7. Return updated user state

**Flash Deals / Auctions / Club Deals (Simulated for Demo):**
- UI shows these in dedicated pages
- Click → "Claim" → coins deducted
- Backend logs as transactions
- No complex auction/bidding logic (would take 2+ hours)
- Focus: User sees the features exist and understands the concept

### 4.4 Gamification Mechanics (5 types)

**1. Scratch Card (✅ Fully Functional)**
- **Probability Distribution:**
  ```
  Try Again: 40% | Small Win (50): 35% | Medium Win (200): 20% | Jackpot (500): 5%
  ```
- **UI:** 3×3 grid, click to reveal, win/lose animation
- **Trigger:** Play anytime (free, just fun)

**2. Spin Wheel (✅ Fully Functional)**
- **Rewards:** 100 / 200 / 300 / 500 coins + bonus multipliers
- **Cost:** 100 coins per spin
- **Trigger:** Click "Spin Wheel" page
- **UI:** Animated wheel, land on reward section, coins awarded

**3. Flash Deals (🎭 Simulated UI)**
- **Features:** Time-limited (shows countdown timer), quantity-limited stock
- **Tier-Gated:** Gold-tier-only flash deals highlighted
- **UI:** Card showing discount, timer, "Claim Now" button
- **Backend:** Click claim → coins deducted, logged as transaction

**4. Easter Eggs (🎭 Simulated)**
- **Example Triggers:**
  - Midnight usage → 200 bonus coins
  - 7-day payment streak → 500 bonus coins + special badge
  - "Konami code" → surprise coin award
- **UI:** Toast notification when triggered
- **Backend:** Logs as special transaction type

**5. Ads (✅ Functional)**
- **Features:** User-initiated video watching
- **Rules:** 3/day cap, max 30 coins total
- **UI:** "Watch Ad" button, shows loading, reward confirmation
- **Backend:** Daily cap enforcement via check_daily_cap()

---

## 5. API Specification

### 5.1 Endpoints

All endpoints return JSON. Base URL: `http://localhost:8000`

#### GET `/health`
Health check.
```json
Response: { "status": "ok" }
```

#### GET `/api/user/{user_id}`
Get user dashboard data (balance, tier, recent transactions, behaviors).
```json
Response: {
  "id": 1,
  "name": "Alex",
  "coin_balance": 1200,
  "tier": "Silver",
  "credit_score": 680,
  "coins_to_next_tier": 1800,
  "behaviors_completed": ["on_time_payment", "savings_milestone"],
  "behaviors_needed_for_next_tier": 2,
  "recent_transactions": [
    {
      "event_type": "on_time_payment",
      "amount": 500,
      "description": "On-time payment",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

#### POST `/api/action`
Trigger a low-risk engagement earning event. High-value financial behaviors are not claimable here; they must be verified through bank, credit bureau, or savings-goal flows.
```json
Request: {
  "user_id": 1,
  "event_type": "education_module"  -- one of: education_module, daily_checkin, ad_watch
}
Response: {
  "success": true,
  "coins_earned": 150,
  "new_balance": 850,
  "new_tier": "Silver",
  "daily_cap_hit": false
}
```

Verified-only financial events: `on_time_payment`, `credit_score_up`, `savings_milestone`, and `direct_deposit` are awarded through `/api/bank/verify-behaviors`, `/api/credit-score`, and `/api/savings-goal/update-progress`. This keeps status and high-value rewards difficult to fake.

#### GET `/api/zkart`
List all products in the marketplace.
```json
Response: {
  "products": [
    {
      "id": 1,
      "name": "Coffee Voucher",
      "category": "food",
      "base_price": 5.0,
      "coin_discount_pct": 10,
      "coins_required": 100,
      "stock": 50
    }
  ]
}
```

#### POST `/api/purchase`
Buy a product with coins.
```json
Request: {
  "user_id": 1,
  "product_id": 1,
  "coins_to_spend": 100
}
Response: {
  "success": true,
  "product_name": "Coffee Voucher",
  "coins_spent": 100,
  "new_balance": 1100,
  "message": "Purchase successful!"
}
```

#### POST `/api/scratch`
Play scratch card game.
```json
Request: { "user_id": 1 }
Response: {
  "result": "small_win",  -- one of: try_again, small_win, medium_win, jackpot
  "coins_won": 50,
  "new_balance": 1150,
  "message": "You won 50 coins!"
}
```

#### POST `/api/spin`
Play the spin wheel (costs 100 coins).
```json
Request: { "user_id": 1 }
Response: {
  "result": "medium_win",
  "coins_won": 300,
  "new_balance": 1050,
  "message": "You won 300 coins!"
}
```

#### GET `/api/flash-deals`
List current flash deals.
```json
Response: {
  "flash_deals": [
    {
      "id": 1,
      "name": "Flight Flash",
      "original_price": 200,
      "flash_price": 150,
      "coins_required": 250,
      "expires_in_seconds": 7200,
      "stock": 3,
      "tier_required": "Silver"
    }
  ]
}
```

#### POST `/api/claim-flash`
Claim a flash deal.
```json
Request: { "user_id": 1, "deal_id": 1 }
Response: {
  "success": true,
  "coins_spent": 250,
  "new_balance": 800,
  "message": "Flash deal claimed!"
}
```

#### GET `/api/auctions`
List live auctions.
```json
Response: {
  "auctions": [
    {
      "id": 1,
      "item_name": "Vintage Watch",
      "current_bid_coins": 500,
      "time_remaining_seconds": 3600,
      "bidders_count": 3
    }
  ]
}
```

#### GET `/api/clubs`
List clubs (for joining) or user's club.
```json
Response: {
  "my_club": {
    "id": 1,
    "name": "Friends",
    "members": ["Alex", "Jordan"],
    "tier": "Silver",
    "shared_coin_pool": 2000
  },
  "suggested_clubs": [
    { "id": 2, "name": "Savers", "members": 4, "tier": "Gold" }
  ]
}
```

#### POST `/api/clubs/create`
Create a new club.
```json
Request: {
  "user_id": 1,
  "club_name": "My Club",
  "description": "We save together"
}
Response: {
  "success": true,
  "club_id": 1,
  "message": "Club created!"
}
```

#### GET `/api/referral-link`
Get user's referral link.
```json
Response: {
  "referral_link": "https://zolve.app/ref/abc123xyz",
  "referrals_count": 2,
  "coins_earned_from_referrals": 600
}
```

#### POST `/api/claim-referral-bonus`
Claim referral bonus (demo: can claim once per session for testing).
```json
Request: { "user_id": 1 }
Response: {
  "success": true,
  "coins_earned": 300,
  "new_balance": 1300,
  "message": "Referral bonus claimed!"
}
```

#### POST `/api/bank/link`
Link a bank account (simulated OAuth flow).
```json
Request: {
  "user_id": 1,
  "bank_name": "HDFC",
  "account_type": "credit_card"
}
Response: {
  "success": true,
  "linked_account_id": 5,
  "bank_name": "HDFC",
  "masked_account": "****5678",
  "authorization_link": "https://hdfc-mock.local/oauth",
  "message": "Ready to verify your transactions"
}
```

#### GET `/api/bank/transactions/{account_id}`
Fetch simulated transactions from mock bank API.
```json
Response: {
  "account_id": 5,
  "transactions": [
    {
      "date": "2024-01-15",
      "description": "Credit Card Payment",
      "amount": 5000,
      "type": "payment",
      "status": "completed",
      "due_date": "2024-01-20",
      "is_on_time": true
    }
  ],
  "last_synced": "2024-01-16T10:30:00"
}
```

#### POST `/api/bank/verify-behaviors`
Detect financial behaviors from linked account data and award coins.
```json
Request: { "user_id": 1, "account_id": 5 }
Response: {
  "detected_behaviors": [
    {
      "type": "on_time_payment",
      "verified": true,
      "coins_awarded": 500,
      "description": "Payment on 2024-01-15 (On-time)",
      "verification_source": "bank_api"
    }
  ],
  "total_coins_awarded": 500,
  "new_balance": 1500
}
```

#### GET `/api/credit-score`
Fetch simulated credit score from mock bureau.
```json
Request: { "user_id": 1 }
Response: {
  "current_score": 680,
  "previous_score": 650,
  "bureau": "Experian",
  "score_improved": true,
  "coins_to_claim": 400,
  "last_updated": "2024-01-16",
  "message": "Your score improved by 30 points! Claim 400 coins."
}
```

#### POST `/api/savings-goal/create`
Create a savings goal (for behavior tracking).
```json
Request: {
  "user_id": 1,
  "goal_name": "Emergency Fund",
  "target_amount": 50000,
  "target_date": "2024-12-31"
}
Response: {
  "goal_id": 1,
  "success": true,
  "message": "Savings goal created!"
}
```

#### POST `/api/savings-goal/update-progress`
Update savings goal progress (simulated or manual input).
```json
Request: {
  "user_id": 1,
  "goal_id": 1,
  "current_amount": 25000
}
Response: {
  "goal_name": "Emergency Fund",
  "progress_percent": 50,
  "milestone_reached": false,
  "coins_awarded": 0,
  "message": "Progress updated!"
}
```

#### GET `/api/verified-behaviors`
Get all verified behaviors for user dashboard.
```json
Response: {
  "verified_behaviors": [
    {
      "behavior_type": "on_time_payment",
      "count": 3,
      "coins_earned": 1500,
      "last_verified": "2024-01-15",
      "status": "verified"
    },
    {
      "behavior_type": "credit_score_up",
      "count": 1,
      "coins_earned": 400,
      "last_verified": "2024-01-16",
      "status": "verified"
    }
  ]
}
```

#### GET `/api/leaderboard`
Top users by coin balance.
```json
Response: {
  "leaderboard": [
    { "rank": 1, "name": "Alex", "coins": 1500, "tier": "Gold" },
    { "rank": 2, "name": "Jordan", "coins": 1200, "tier": "Silver" }
  ]
}
```

---

## 6. Frontend: Streamlit Pages (9 Pages)

### 6.1 Page Structure (9 Pages)

**Sidebar Navigation:**
1. Home (Dashboard)
2. **Link Bank** (behavioral tracking setup) — NEW
3. Earn (9 earning events)
4. Z-Kart (marketplace)
5. Games (scratch card + spin wheel)
6. Flash Deals (time-limited offers)
7. Auctions (demo auction showcase)
8. Z-Clubs (club creation + leaderboard)
9. Profile (referrals, easter eggs, history)

### 6.2 Page Details

#### Page 1: Dashboard (`/`)
- **Hero Card:** Display user name, tier badge (with color), coin balance in large font
- **Tier Progress Bar:** Visual bar showing distance to next tier (e.g., "1200 / 3000 coins to Gold")
- **Recent Activity Feed:** Last 10 coin transactions (earn/spend) with timestamps
- **Behaviors Checklist:** Visual list of completed behaviors, grayed out if not done

**Key UX:**
- Animated coin counter (number animates when balance changes)
- Tier badge changes color: gray (Basic) → silver shimmer (Silver) → gold (Gold)

#### Page 2: Link Bank (`/link-bank`) — BEHAVIOR VERIFICATION
**Critical page for real behavior tracking.**

- **Tab 1: Link Account**
  - "Select your bank" dropdown: HDFC, ICICI, Axis, SBI, Kotak
  - "Enter account number" (simulated, masked display)
  - "Authorize access" button → mock OAuth flow
  - Shows: "Connecting to your bank..." → "✓ Connected!"
  - Displays linked account summary

- **Tab 2: Verified Behaviors**
  - Auto-fetched from mock bank API
  - Shows detected financial behaviors:
    1. **On-Time Payments** (past 3 months)
       - "Jan 15: Credit card payment ₹5000 [ON-TIME] +500 coins ✓"
       - "Jan 10: EMI payment ₹2000 [ON-TIME] +500 coins ✓"
    2. **Credit Score** (fetched from mock Experian)
       - "Current score: 680 (up from 650) +400 coins ✓"
       - Shows date of last check
    3. **Savings Progress** (from linked account)
       - "Savings account balance: ₹25,000"
       - "Goal: ₹50,000 for emergency fund"
       - Progress bar: 50% complete

- **Tab 3: Sync History**
  - Shows when bank data was last synced
  - "Sync Now" button → fetches latest data → checks for new behaviors
  - If new behavior detected → coins awarded automatically
  - Toast: "Payment verified! +500 coins awarded"

- **Visual Feedback:**
  - Verified behaviors show ✓ badge
  - Coin awards shown inline
  - Clear "Connected" status indicator
  - Real-time updates as API calls return

#### Page 3: Earn (`/earn`)
- **9 Action Cards** in a grid layout (all from spec):
  1. On-time Payment (500 coins) — verified via Link Bank — ✅ Verified, not manually claimable
  2. Credit Score Increase (400 coins) — verified via mock bureau — ✅ Verified, not manually claimable
  3. Savings Milestone (350 coins) — verified via savings goal progress — ✅ Verified, not manually claimable
  4. Direct Deposit (200 coins) — verified via linked account data — ✅ Verified, not manually claimable
  5. Education Module (150 coins) — Unlimited — ✅ Functional
  6. Daily Check-in (50 coins) — 1/day cap — ✅ Functional
  7. Watch Ad (10 coins) — 3/day cap — ✅ Functional
  8. Referral Link (300 coins) — Shows "invite friends" modal — 🎭 Simulated
  9. Easter Egg Hint — Shows hint for hidden trigger — 🎭 Simulated
- Verified financial cards show: icon, description, coin reward, verification source, and a "Verify in Link Bank" or "View Status" button.
- Engagement cards show: icon, description, coin reward, daily cap status, and a "Claim" button.
- **Daily cap indicator:** Disabled buttons show "Next: [date]" or "Unlimited"
- On claim/verification → toast notification + balance updates live + transaction logged

#### Page 4: Z-Kart (`/zkart`)
- **Product Grid:** 3 columns of product cards
- **Card Design:** Image placeholder, name, base price, coin discount badge, "Buy with Coins" button
- **Filter:** Dropdown to filter by category (All, Food, Travel, Retail, Entertainment)
- **Purchase Modal:** On click, confirm dialog shows:
  - Product name, price, coins required
  - Button: "Spend X coins" or "Not enough coins"
  - On success → item removed from stock, balance updates

#### Page 5: Games (`/games`)
- **Tab 1: Scratch Card**
  - 3×3 grid of hidden cells (CSS cards with `?` symbol)
  - Click cell → reveal animation → shows result (try-again ❌ / win amounts)
  - Result modal: "Try Again" or "You won X coins!" + new balance
  - Free to play, unlimited times

- **Tab 2: Spin Wheel**
  - Large animated wheel with 6 segments: 100 / 200 / 300 / 500 / 2x Multiplier / Free Spin
  - Cost: 100 coins per spin
  - Click "Spin" → wheel animates → lands on reward → coins awarded
  - History of last 5 spins shown below

#### Page 6: Flash Deals (`/flash-deals`)
- **Limited-time Offers:** 4-6 flash deal cards
- **Each card shows:**
  - Product/offer name
  - Original price vs. flash price
  - Countdown timer (e.g., "Expires in 2:45:30")
  - Stock counter (e.g., "3 / 10 remaining")
  - Coin cost to claim
  - Tier requirement badge (e.g., "Silver+" required)
- **Mechanic:** Click "Claim Now" → coin deduction → product added to claimed inventory
- **Backend:** Simple list of flash deals, simulated timer

#### Page 7: Auctions (`/auctions`)
- **Live Auctions:** 3-4 auction listings
- **Each shows:**
  - Item name + image placeholder
  - Current bid (in coins)
  - Time remaining countdown
  - Number of bidders
  - "Place Bid" button (simulated, non-functional but shows UI)
- **Auction History:** Completed auctions, showing winner + final price
- **Note:** This is a SHOWCASE/DEMO page. No actual bidding logic (too complex for 5 hours)

#### Page 8: Z-Clubs (`/clubs`)
- **Tab 1: Create/Join Club**
  - Form to create new club: name, description, 2-6 member selection
  - "Create Club" button (simulated, shows confirmation)
  - List of suggested clubs to join with "Join" button

- **Tab 2: My Club** (if in a club)
  - Club name, members, shared coin pool (visualization)
  - Club tier badge: Bronze / Silver / Gold based on members
  - Club quests: "Make 3 purchases together" with progress bar
  - Club leaderboard: Members ranked by individual coin balance

- **Tab 3: Club Deals**
  - Group purchase offers (e.g., "Coffee for 2 people, 150 coins total")
  - Show minimum members needed, current interest count
  - "Join Group Purchase" button (simulated)

#### Page 9: Profile (`/profile`)
- **Personal Stats:**
  - Total coins earned (lifetime)
  - Total coins spent
  - Behavior completion rate (x/9 actions completed)
  - Favorite category in Z-Kart
  - Power user badge (if triggered easter egg)

- **Referral Dashboard:**
  - Unique referral link (simulated)
  - "Friends Invited: X" counter
  - Coins earned from referrals: X

- **Easter Eggs:**
  - "Mystery Trigger Hints" section
  - Shows clues like "🌙 Active at midnight?" or "7️⃣ Consistent payments?"

- **Full Transaction History:**
  - Sortable table: Date | Event | Coins | Balance
  - Filter by event type

---

## 7. Design System: CRED-Inspired Dark Theme

### 7.1 Color Palette

```css
--bg-primary: #0A0A0A          /* Main background */
--bg-secondary: #111111        /* Subtle depth */
--bg-card: rgba(255,255,255,0.04)  /* Card background (glassmorphism) */

--accent-gold: #D4AF37         /* Premium, tier badge */
--accent-purple: #8B5CF6       /* Highlight, hover states */
--accent-green: #10B981        /* Success, earnings */
--accent-red: #EF4444          /* Loss, spending */

--text-primary: #FFFFFF        /* Main text */
--text-muted: #6B7280          /* Secondary text */
--border: rgba(255,255,255,0.08)  /* Subtle borders */
```

### 7.2 Card Style (Glassmorphism)

```css
.card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  padding: 20px;
  transition: all 0.3s ease;
}

.card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(212, 175, 55, 0.3);
}
```

### 7.3 Tier Badges

```css
.tier-basic {
  background: linear-gradient(135deg, #6B7280, #4B5563);
  color: #FFFFFF;
}

.tier-silver {
  background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
  color: #1a1a1a;
}

.tier-gold {
  background: linear-gradient(135deg, #D4AF37, #AA8C51);
  color: #1a1a1a;
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}
```

### 7.4 Animations

- **Coin counter:** Number changes with brief spin animation
- **Card hover:** Subtle blur increase + border glow
- **Button press:** Scale down 0.95, then back to 1
- **Scratch reveal:** 0.3s fade-in from bottom

---

## 8. File Structure

```
zolve/
├── backend/
│   ├── main.py               # FastAPI app, 12+ endpoints
│   ├── database.py           # SQLite setup, schema, seed
│   ├── models.py             # Pydantic request/response models
│   └── game_engine.py        # Coin logic, tier calc, games, flash deals
├── frontend/
│   ├── app.py                # Streamlit multi-page app (9 pages)
│   └── style.css             # CRED dark theme (injected via st.markdown)
├── requirements.txt
├── system_design.md          # This file
└── zolve.db                  # SQLite database (auto-created)
```

---

## 9. Implementation Order (5-Hour Timeline — Breadth Focus with Behavior Tracking)

**Strategy:** Build backend first (fully), then UI pages (basic → interactive)

**🔴 CRITICAL:** Bank linking (Page 2) is now a CORE feature—not optional.

| Time | Task | Focus |
|------|------|-------|
| 0:00–0:25 | Setup: `requirements.txt`, directories, `database.py` + **full schema INCLUDING behavior tables** | All earning/spending/game + bank/credit/savings tables |
| 0:25–1:15 | `game_engine.py`: all 9 coin events, all 5 games, tier logic, **behavior verification logic** | Core logic + mock bank API responses |
| 1:15–2:15 | `main.py`: 18+ FastAPI endpoints (earn, spend, games, **bank linking, behavior verification**, flash, auctions, clubs) | All routes, mock bank/credit bureau API |
| 2:15–2:30 | `models.py`: Pydantic models for all request/response types (including bank data) | Complete schemas |
| 2:30–3:10 | `frontend/app.py` Pages 1-3 (Dashboard, **Link Bank, Earn**) | CRITICAL: Bank linking is priority |
| 3:10–3:50 | `frontend/app.py` Pages 4-5 (Z-Kart, Games) | Fully functional commerce + games |
| 3:50–4:20 | `frontend/app.py` Pages 6-9 (Flash, Auctions, Clubs, Profile) | Showcase UI + simulated data |
| 4:20–4:45 | `style.css`: CRED dark theme, glassmorphism across all pages | Consistent branding |
| 4:45–5:00 | Integration testing + demo data seeding (bank accounts, verified behaviors) | Full flow validation |

**Priority Change:** Bank linking moved earlier because it's core to the system's value prop.

---

## 10. Key Design Decisions: Breadth with Simulation

### 10.1 "Breadth with Simulation" Strategy
In 5 hours, you can't build everything fully. So we show EVERYTHING (9 pages, all features from spec) but vary the depth:

**✅ Fully Functional (100% logic implemented):**
- Earning engine (all 9 events, daily caps)
- Tier system (real-time progression)
- Z-Kart marketplace (real transactions)
- Scratch card & spin wheel (probability engines)
- Ad watching (capped at 3/day)

**🎭 Simulated/UI-Focused (Logic simplified, data mocked):**
- Flash deals (timers shown, claims work, but no real scarcity)
- Auctions (display only, no actual bidding logic)
- Z-Clubs (creation UI works, leaderboard shows mock data)
- Referrals (shows link, can claim bonus, but no real referral tracking)
- Easter eggs (1 hidden trigger implemented, hints shown for others)
- Price comparison (mocked API response)

**Key Insight:** A user looking at the demo sees the FULL ECOSYSTEM. They understand the vision even if some parts are simplified for the prototype. This is more impressive than a "perfect" partial implementation.

### 10.2 Why This Mix?
- **Breadth:** Shows stakeholders/investors the full vision (all 6 layers of spec)
- **Depth where it matters:** Core earning/spending/game loops are bulletproof (the soul of the system)
- **Time-efficient:** Simulated features look polished but take 20% of the time of full implementation
- **Demo-ready:** User can see the complete story in 8 minutes

### 10.3 Simulated Features: What That Means in Practice

**Auctions Example:**
- **Real:** GET `/api/auctions` returns 3 auction listings with realistic data
- **Simulated:** No actual bidding. "Place Bid" button is UI-only
- **Coin Cost:** Claiming an auction DOES deduct coins and log transaction
- **Benefit:** Looks complete in demo, takes 20 min to build instead of 2 hours

**Referrals Example:**
- **Real:** User gets unique referral link (generated from user_id)
- **Real:** Clicking "Claim Referral Bonus" (for demo) → 300 coins earned
- **Simulated:** No actual referral tracking; can claim infinite times in demo
- **Benefit:** Shows the feature, rewards work, but no complex referral graph logic

**Easter Eggs Example:**
- **Real:** Hidden trigger "Pay 7 days in a row" → 500 bonus coins
- **Simulated:** "Easter Egg Hints" page shows clues; user can manually trigger for demo
- **Benefit:** Concept is clear, behavior evident, but no complex trigger detection

### 10.4 Why SQLite?
Zero setup, file-based, sufficient for demo. No Docker, no external DB server needed. Scales to ~100K transactions before performance issues.

### 10.5 Why FastAPI over Flask?
Faster startup, Pydantic built-in (no extra validation code), async-ready (though sync OK for this scope). Modern Python standard.

### 10.6 Why Streamlit?
Rapid UI prototyping. No frontend build step. CSS injection works. Great for demos. **Trade-off:** Not production-grade, but perfect for hackathon.

### 10.7 Why Raw SQL over ORM?
No setup time for SQLAlchemy. Raw `sqlite3` is 50 LOC faster to write than declarative models. Acceptable for a 5-hour MVP.

### 10.8 Why CRED-Inspired Design?
Mirrors target user expectations (modern fintech). Dark + glassmorphic = premium feel without complex animations. Inject via Streamlit's `st.markdown(..., unsafe_allow_html=True)`.

---

## 11. Success Criteria (Verification Checklist)

### Backend (Fully Functional)
- [ ] `uvicorn backend.main:app --reload` starts without error
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] All 9 earning events are represented with correct routing: verified financial behaviors via bank/credit/savings flows; capped engagement actions via `/api/action`; simulated growth/exploration clearly labeled
- [ ] `POST /api/action` returns correct coins only for low-risk engagement event types
- [ ] User tier upgrades: Basic (0) → Silver (1000+ + 2 behaviors) → Gold (3000+ + 5 behaviors)
- [ ] Caps enforced across earning paths (verified financial behavior frequency limits, checkin 1/day, ads 3/day max)
- [ ] `POST /api/scratch` probability distribution works (40/35/20/5 split)
- [ ] `POST /api/spin` returns 6 possible rewards
- [ ] `POST /api/purchase` deducts coins correctly
- [ ] Flash deals, auctions, clubs endpoints return proper JSON

### Frontend (9 Pages)
- [ ] `streamlit run frontend/app.py` starts without error
- [ ] **Page 1 (Dashboard):** User name, balance, tier badge, progress bar, activity feed (10 transactions)
- [ ] **Page 2 (Link Bank):** Mock account linking, verified behavior detection, credit score verification, automatic coin awards
- [ ] **Page 3 (Earn):** 9 earning options shown; high-value financial actions route to verification, low-value engagement actions are claimable with caps
- [ ] **Page 4 (Z-Kart):** Product grid (8 items), category filter, purchase flow, stock updates
- [ ] **Page 5 (Games):** Tab 1 (Scratch - 3×3 grid, reveals work), Tab 2 (Spin Wheel - animated, rewards shown)
- [ ] **Page 6 (Flash Deals):** 4 deal cards with countdown timers, claim buttons work
- [ ] **Page 7 (Auctions):** 3 live auctions showing bid, time, bidders (UI only, simulated)
- [ ] **Page 8 (Z-Clubs):** Club creation form, club leaderboard, club deals showcase
- [ ] **Page 9 (Profile):** Stats, referral link, easter egg hints, full transaction history
- [ ] Navigation works between all 9 pages via sidebar
- [ ] CRED dark theme visible (gold accents, glassmorphic cards, smooth animations)

### End-to-End Demo Flow
- [ ] Earn coins via multiple paths (actions, games, simulated features all show)
- [ ] Tier progression visualized in real-time
- [ ] Spend coins in marketplace, games, flash deals
- [ ] All transactions logged and visible in history
- [ ] Can navigate full ecosystem in <5 minutes
- [ ] UI tells the complete story: behavior → coins → status → commerce → games → social

---

## 11.5 Frontend Page Coverage (9 Pages)

| Page | Features Shown | Functional % | Notes |
|------|----------------|--------------|-------|
| 1. Dashboard | User profile, tier, balance, activity feed | 100% | Real-time updates |
| 2. **Link Bank** | Account linking, verified behaviors (CORE) | 100% | Mock bank API, credit bureau |
| 3. Earn | 9 earning options, capped engagement claims, verification routing | 100% | High-value financial behaviors are verified in Link Bank/credit/savings flows |
| 4. Z-Kart | Product grid, filtering, purchases | 100% | Fully functional commerce |
| 5. Games | Scratch card + Spin wheel + probability | 100% | Real probability engine |
| 6. Flash Deals | Time-limited offers, tier gates | 75% | UI + simulated timers |
| 7. Auctions | Live auctions display, bid viewing | 30% | UI showcase only |
| 8. Z-Clubs | Club creation, leaderboard, deals | 40% | UI + mock data |
| 9. Profile | Stats, referrals, easter eggs, history | 80% | UI + simulated features |

**Key Addition (Page 2 - Link Bank):** This page TRANSFORMS the system from "free coin vending machine" to "real behavior verification system."

---

## 12. Demo Script (10-Minute Full Ecosystem Walkthrough)

**Narrative:** "Zolve is a behavioral operating system that VERIFIES financial discipline. Link your bank → we detect good behavior → you earn coins → unlock rewards."

```
PART 0: THE VERIFICATION LAYER (2 min) — CRITICAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Dashboard
   → Show user: "Alex", Basic tier, 0 coins
   → Note: "Bank account not linked" banner

2. Link Bank page (NEW — THE KEY DIFFERENTIATOR)
   → Click "Select Bank" → Choose "HDFC"
   → Input account number (simulated)
   → Click "Authorize" → mock OAuth flow
   → Shows "✓ Connected successfully!"
   → Tab: "Verified Behaviors" shows detected transactions:
      • "Jan 15: Credit card payment ₹5000 [ON-TIME] +500 coins ✓"
      • "Jan 10: EMI payment ₹2000 [ON-TIME] +500 coins ✓"
   → Tab: "Credit Score" shows:
      • "Current: 680 (up from 650) +400 coins ✓"
   → Balance JUMPS from 0 → 1400 coins automatically
   → **This is the aha moment:** "We detect your good behavior automatically"

3. Back to Dashboard
   → Tier flipped to SILVER (1400 coins + 2 verified behaviors)
   → Activity feed shows verified behavior coins

PART 1: THE ECOSYSTEM (3 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. Earn page
   → Show 9 earning options (all from spec)
   → High-value financial actions show "Verified in Link Bank" status, not free claim buttons
   → Click Education Module (+150) and Daily Check-in (+50)
   → Watch Ad (+10, capped)
   → Balance updates from verified baseline, toast notifications confirm capped engagement rewards

3. Dashboard updated
   → Tier: Silver, driven by bank-verified behaviors
   → Activity feed separates verified financial rewards from low-value engagement rewards

PART 2: COMMERCE & GAMIFICATION (3 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. Z-Kart Marketplace
   → Browse product grid (8 items)
   → Show category filter
   → Select "Flight Credit" ($200)
   → Purchase with 400 coins → Balance: 1050

5. Games page (Tab 1: Scratch)
   → Show 3×3 grid
   → Click 3 cells → "Try Again" → "You won 200 coins!"
   → Balance: 1250, toast notification

6. Games page (Tab 2: Spin Wheel)
   → Cost: 100 coins per spin
   → Click Spin → animated wheel → lands on "300 coins"
   → Balance: 1450

PART 3: BREADTH — FULL ECOSYSTEM (3 min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. Flash Deals
   → Show 4 time-limited offers with countdowns
   → Highlight Silver-tier-only deals
   → Click "Claim" on one → coins deducted

8. Auctions
   → Show 3 live auction items
   → Show "Current bid", "Time remaining", "Bidders"
   → Explain: "Competitive way to spend coins"

9. Z-Clubs
   → Show club creation form
   → Display: "Bronze club (1 member)" badge
   → Show club leaderboard
   → Explain: "Peer pressure drives financial discipline"

10. Profile
    → Show lifetime stats: "2500 coins earned, 1000 spent"
    → Show referral link: "Invite friends, earn 300 coins each"
    → Show easter egg hint: "🌙 Active at midnight? Try something special..."
    → Show full transaction history (10+ entries, filterable)

CLOSING
━━━━━━━
→ Back to Dashboard
→ Show tier: Silver, 1450 coins, final activity feed
→ "This is behavioral lock-in. Users keep coming back because:
   1. Daily earning opportunities (7 actions)
   2. Multiple spending paths (6 sinks)
   3. Gamification keeps it fun (5 mechanics)
   4. Social pressure via clubs (2-6 member groups)
   5. Mystery (easter eggs, power-user badges)
   All of this data trains a financial AI."
```

---

## 13. Production Considerations (Out of Scope)

- Authentication & authorization
- Multi-user support with concurrent writes
- Data encryption at rest
- API rate limiting
- Monitoring & observability
- Z-Clubs & social features
- Price comparison & external APIs
- Mobile-first responsive design
- Unit & integration tests
- CI/CD pipeline

All deferred to Phase 2+.

---

## 14. Appendix: Code Style Guidelines

See `CLAUDE.md` for full coding standards. Key points for this project:

- **No premature abstraction.** Simple functions > over-engineered classes.
- **Defensive validation:** All external inputs checked (API requests, DB reads).
- **Clear naming:** `calculate_tier()` not `calc_t()`.
- **Error handling:** Explicit HTTP status codes + error messages.
- **Logging:** Brief, not spammy. No secrets in logs.
- **DRY but pragmatic:** 3 similar lines is fine. Don't invent helpers for one call.

---

**Last Updated:** 2026-04-29  
**Prepared for:** Zolve Hackathon (5-hour build)  
**Prepared by:** Senior Engineering (Claude Code)
