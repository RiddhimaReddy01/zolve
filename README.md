# Zolve MVP — Behavioral Finance Gamification Platform

> **A 5-hour hackathon MVP demonstrating a behavioral finance ecosystem where verified financial actions drive real progress.**

## 🎯 What is Zolve?

Zolve is a **behavioral finance gamification platform** that:

1. **Verifies financial behaviors** via mock bank APIs (on-time payments, credit score improvements, savings milestones)
2. **Awards coins automatically** when behaviors are detected (no fake "claim free coins" problems)
3. **Ties coins to tier progression** (Basic → Silver → Gold), where tiers require BOTH coins AND verified behaviors
4. **Provides multiple spending sinks** (Z-Kart marketplace, games, flash deals, auctions, clubs) to prevent inflation
5. **Logs all activity** to SQLite for behavioral profiling and future credit/lending products

### Why This Matters

Traditional gamification in fintech feels exploitative: scratch cards, daily streaks, FOMO deals. Zolve flips this by:
- Rewarding **real financial discipline** (on-time payments, savings, credit improvement)
- Making coins **meaningful** (tied to tier progression, not just cosmetic)
- Creating **sustainable engagement** (behaviors drive progress, not habit manipulation)

---

## 🏗️ Architecture

### Backend (FastAPI + SQLite)

```
backend/
├── main.py                  # FastAPI entry point (19 endpoints)
├── routes/                  # Modularized route modules
│   ├── coins.py            # Earning & balance endpoints
│   ├── marketplace.py       # Z-Kart commerce
│   ├── games.py            # Scratch card & spin wheel
│   └── bank.py             # Bank linking & verification
├── game_engine.py          # Business logic (coin calc, tier progression, games)
├── database.py             # SQLite connection & schema (9 tables)
├── models.py               # Pydantic validators (11 models)
├── constants.py            # Extracted magic numbers (50+ constants)
└── exceptions.py           # Custom exception hierarchy (8 exceptions)
```

**Database Schema:**
```sql
users (id, name, email, coin_balance, tier, credit_score)
coin_transactions (user_id, amount, event_type, description, created_at)
behaviors (user_id, behavior_type, verified, verification_source, behavior_data)
linked_accounts (user_id, bank_name, account_number, account_id, linked_at)
bank_transactions (account_id, transaction_date, description, amount, is_on_time)
credit_score_history (user_id, score, score_date, bureau, fetched_at)
savings_goals (user_id, goal_name, target_amount, current_amount)
products (id, name, category, base_price, coin_discount_pct, coins_required)
purchases (user_id, product_id, coins_spent, price_paid, created_at)
```

### Frontend (Streamlit)

```
frontend/
├── app.py                   # Multi-page Streamlit app
└── (9 pages)
    ├── Dashboard           # Profile, balance, tier, activity feed
    ├── Link Bank          # Account linking, behavior verification
    ├── Earn               # 9 earning actions (verified + engagement)
    ├── Z-Kart             # Marketplace, product grid, purchases
    ├── Games              # Scratch card, spin wheel
    ├── Flash Deals        # Time-limited tier-gated offers
    ├── Auctions           # Live bidding showcase
    ├── Z-Clubs            # Social clubs & leaderboards
    └── Profile            # Stats, verified behaviors, transaction history
```

**Styling:** CRED-inspired dark theme with glassmorphism cards, gold/purple accents, tier color coding.

### API Endpoints (19 total)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/user/{user_id}` | GET | Dashboard data |
| `/api/tier-progress/{user_id}` | GET | Tier progression |
| `/api/verified-behaviors/{user_id}` | GET | Verified behavior history |
| `/api/leaderboard` | GET | Top users by coins |
| `/api/coins/earn` | POST | Earn coins for action |
| `/api/coins/balance/{user_id}` | GET | Check balance |
| `/api/coins/history/{user_id}` | GET | Transaction history |
| `/api/bank/link` | POST | Link bank account |
| `/api/bank/transactions/{user_id}` | GET | Bank transaction data |
| `/api/bank/verify-behaviors/{user_id}` | POST | Detect & award verified behaviors |
| `/api/bank/credit-score/{user_id}` | GET | Credit score data |
| `/api/zkart/products` | GET | List products |
| `/api/zkart/products/{product_id}` | GET | Product details |
| `/api/zkart/purchase` | POST | Buy with coins |
| `/api/zkart/categories` | GET | Product categories |
| `/api/games/scratch` | POST | Play scratch card |
| `/api/games/spin` | POST | Play spin wheel |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone/Download the project:**
   ```bash
   cd zolve
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

**Terminal 1: Start Backend (FastAPI)**
```bash
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Terminal 2: Start Frontend (Streamlit)**
```bash
cd frontend
streamlit run app.py
```

Output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Open in Browser:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📊 Demo Walkthrough

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for a comprehensive 5-minute demo script with:
- What to show in each page
- Key messages to emphasize
- Technical Q&A talking points
- Contingency plans if something breaks

**Quick Demo Flow:**
1. **Dashboard** — Show 1,600 coins from verified behaviors (not manual claims)
2. **Link Bank** — Link ICICI account, system detects on-time payments
3. **Earn** — Show 9 earning actions, claim daily check-in (+50 coins)
4. **Z-Kart** — Browse products, buy Starbucks gift card (-250 coins)
5. **Games** — Play scratch card, win coins
6. **Dashboard** — Show tier progression to Silver (1000+ coins + 2 behaviors)

---

## 💡 Key Features

### 1. **Verified Earning (Core Differentiator)**

```
User Links Bank Account
    ↓
Mock Bank API Returns Transaction Data
    ↓
System Detects: "On-time payment on Jan 15" ✓
    ↓
System Awards: +500 coins AUTOMATICALLY
    ↓
User Sees: "On-time Payment (₹5000 on 2024-01-15) [+500 coins]" in verified behaviors
```

**Why this matters:** Users can't spam "claim coins" for free. Real behaviors drive coins.

### 2. **Tier System with Dual Requirements**

```
Basic:  0-999 coins (no behavior requirement)
Silver: 1000+ coins AND 2+ verified behaviors
Gold:   3000+ coins AND 5+ verified behaviors
```

**Why this matters:** Coins alone aren't enough. Users must demonstrate financial discipline via verified behaviors.

### 3. **Multiple Earning Paths**

| Type | Method | Example | Coins | Verified? |
|------|--------|---------|-------|-----------|
| **Verified Financial** | Bank API | On-time payment | 500 | ✅ |
| **Verified Financial** | Credit bureau | Credit score ↑ | 400 | ✅ |
| **Verified Financial** | User goal | Savings milestone | 350 | ✅ |
| **User-Initiated** | Self-report | Education module | 150 | ⚠️ |
| **Engagement** | Habit | Daily check-in | 50 | ❌ |
| **Gamification** | Luck | Scratch card win | 0-500 | ❌ |

### 4. **Commerce Integration**

8 products across categories (Food, Travel, Retail, Entertainment) with:
- Base price (₹)
- Coin cost (coins required)
- Discount % (additional % off with coins)

Example: Starbucks ₹500 → 250 coins with +10% coin discount

### 5. **Gamification (Balanced)**

- **Scratch Card** (free): 40% try_again, 35% +50, 20% +150, 5% +500
- **Spin Wheel** (100 coins): 6 segments [50, 100, 200, 300, 500, 1000]

Design philosophy: Games are for **engagement**, not primary earning. Real behaviors drive progress.

---

## 📈 Key Metrics

| Metric | Value |
|--------|-------|
| **Earning Actions** | 9 (4 verified financial, 3 engagement, 2 gamification) |
| **Commerce Options** | 8 Z-Kart products |
| **Database Tables** | 9 (comprehensive schema) |
| **API Endpoints** | 19 (fully modularized) |
| **Code Quality** | Type hints, Pydantic validators, exception hierarchy (CLAUDE.md standards) |
| **Demo Time** | 5 minutes (full user journey) |

---

## 🎓 Code Quality (CLAUDE.md Standards)

### Phase 0: Structural Setup ✅

- ✅ **Split routes into 4 modules** (coins, marketplace, games, bank)
- ✅ **Exception hierarchy** (8 custom exceptions)
- ✅ **Constants extracted** (50+ magic numbers → constants.py)
- ✅ **Database class** (context managers, dependency injection)
- ✅ **Pydantic validators** on all inputs
- ✅ **Type hints** on all functions
- ✅ **Streamlit modularized** (9-page app with state management)

### Phase 1: Core Implementation ✅

- ✅ **Database schema** (9 tables, properly indexed)
- ✅ **Game engine** (coin logic, tier calculation, behavior verification)
- ✅ **API endpoints** (19 fully tested)
- ✅ **Bank verification** (mock API with realistic data)
- ✅ **Frontend pages** (all 9 pages implemented)

### Phase 2: Experience ✅

- ✅ **Frontend UI** (CRED dark theme, glassmorphism cards)
- ✅ **End-to-end testing** (full user journey works)
- ✅ **Demo script** (comprehensive walkthrough)

---

## 🧪 Testing

### End-to-End Test

Run the complete user journey:

```bash
bash /tmp/test_journey.sh  # See output above
```

Or manually:

```bash
# 1. Get user dashboard
curl http://localhost:8000/api/user/1

# 2. Earn coins
curl -X POST http://localhost:8000/api/coins/earn \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "action_type": "on_time_payment"}'

# 3. Link bank
curl -X POST http://localhost:8000/api/bank/link \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "bank_name": "HDFC", "account_number": "1234567890"}'

# 4. Verify behaviors
curl -X POST http://localhost:8000/api/bank/verify-behaviors/1

# 5. Purchase product
curl -X POST http://localhost:8000/api/zkart/purchase \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 1, "coins_to_spend": 250}'

# 6. Play game
curl -X POST http://localhost:8000/api/games/scratch \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

---

## 📚 Documentation

- **[system_design.md](system_design.md)** — Complete technical architecture (6 layers, 18+ endpoints, database schema)
- **[BEHAVIOR_TRACKING.md](BEHAVIOR_TRACKING.md)** — Detailed explanation of verified behavior system
- **[ALIGNMENT.md](ALIGNMENT.md)** — Feature mapping to project_instructions.md
- **[VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)** — Comprehensive verification report (3 agents, spec/code quality/problem fit)
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** — 5-minute demo walkthrough with talking points
- **[CLAUDE.md](../CLAUDE.md)** — Code quality standards (all followed)

---

## 🎯 Product Roadmap

### Phase 1: MVP (5 hours) ✅
- Core earning system (9 actions)
- Bank verification (mock API)
- Marketplace (8 products)
- Games (scratch, spin)
- Dashboard & tier progression
- Code structure (modularized, type-safe)

### Phase 2: Full Features (Post-Hackathon)
- Real bank API integrations (Open Banking, OAuth)
- Multi-user Z-Clubs with real sync
- Price comparison engine
- Advanced easter egg triggers
- Admin dashboard

### Phase 3: Analytics & Intelligence
- Behavioral profiling dashboard
- Credit score modeling
- Retention prediction
- Engagement optimization

### Phase 4: Lending & Scale
- Credit scoring for lending
- Micro-loan products
- Referral network effects
- Platform scaling

---

## 💰 Business Model

1. **Take-rate on Z-Kart** — Users save 5-10% with coins, we negotiate bulk discounts with brands
2. **Data licensing** — Anonymized behavioral profiles to fintech companies
3. **Lending** — Credit products for high-tier users (proven financial discipline)
4. **Premium features** — Exclusive earning actions, higher coin rewards for paid users

---

## 🔐 Security & Data

- **No real bank data stored** (MVP uses mock API)
- **No sensitive data exposed** (passwords, tokens never logged)
- **SQLite for demo** (would use PostgreSQL in production)
- **Parameterized queries** (no SQL injection risk)
- **Input validation** (Pydantic validators on all endpoints)

---

## 🎨 Design System

### Colors (CRED-inspired dark theme)
- **Background Primary:** #0A0A0A (pure black)
- **Card Background:** rgba(255,255,255,0.04) with backdrop blur
- **Accent Gold:** #D4AF37 (tier rewards)
- **Accent Purple:** #8B5CF6 (highlights)
- **Text Primary:** #FFFFFF (white)
- **Text Muted:** #6B7280 (gray for secondary text)

### Tier Color Coding
- **Basic:** #6B7280 (gray)
- **Silver:** #C0C0C0 (silver shimmer)
- **Gold:** #D4AF37 (gold gradient)

### Cards
- Glassmorphism: `background: rgba(255,255,255,0.04); backdrop-filter: blur(12px); border-radius: 16px;`
- Shadow: `box-shadow: 0 8px 32px rgba(0,0,0,0.4);`
- Border: `1px solid rgba(255,255,255,0.08);`

---

## 🚀 Deployment

For production deployment:

1. **Backend:** Deploy FastAPI on Heroku/AWS Lambda/Google Cloud Run
2. **Frontend:** Deploy Streamlit on Streamlit Cloud or as Docker container
3. **Database:** Migrate from SQLite to PostgreSQL
4. **APIs:** Integrate real bank APIs (HDFC, ICICI, Axis)
5. **Auth:** Add user authentication (OAuth, JWT)

---

## 📞 Support

For questions or issues:
- Check [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for common Q&A
- Review [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md) for design rationale
- See [system_design.md](system_design.md) for technical details

---

## 📜 License

MIT License — Feel free to use, modify, and distribute.

---

**Built in 5 hours for the Zolve Hackathon. Questions? Let's talk! 🚀**
