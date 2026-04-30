# Zolve MVP — 5-Minute Demo Script

## What is Zolve?

Zolve is a **behavioral finance gamification platform** that rewards users for financial discipline through a verified coin economy. Unlike traditional rewards apps that let users "claim free coins," Zolve:

1. **Verifies behaviors** via bank APIs (on-time payments, credit score improvements)
2. **Awards coins automatically** when behaviors are detected
3. **Ties coins to real progress** (tier progression, credit improvement)
4. **Creates a sustainable loop** — behavior → coins → tier → benefits → more discipline

---

## System Architecture

```
User Links Bank → Mock Bank API Fetches Transactions
                ↓
        Detects: "On-time Payment on Jan 15" ✓
        System Awards: +500 coins automatically
                ↓
        User Tier Upgrades: Basic → Silver (1000+ coins + 2 behaviors)
                ↓
        User Can: Spend coins in Z-Kart, play games, claim more actions
                ↓
        Activity Logged: Full audit trail in database
```

**Core Loop:** Financial Behavior → Verified Earning → Tier Progression → Spending/Engagement → More Discipline

---

## 5-Minute Demo Walkthrough

### Setup (Before Demo)

**Terminal 1: Start Backend**
```bash
cd backend
python -m uvicorn main:app --reload
# Runs on http://localhost:8000
# Health check: curl http://localhost:8000/health
```

**Terminal 2: Start Frontend**
```bash
cd frontend
streamlit run app.py
# Runs on http://localhost:8501
# Open in browser: http://localhost:8501
```

---

### Demo Flow (5 minutes)

#### **Minute 0-1: Dashboard — Show Initial State**

Navigate to **Dashboard** page.

**What to highlight:**
- User: "Demo User" (demo@zolve.app)
- Balance: 1,600 💰 (from verified bank behaviors)
- Tier: **Silver** ⭐ (achieved after bank verification)
- Verified Behaviors: **3** ✅
  - On-time Payment (₹5000 on 2024-01-15) → +500 coins
  - Direct Deposit (₹50,000 on 2024-01-05) → +200 coins
  - Credit Score Improvement (650 → 834) → +400 coins

**Key message:** "Users didn't click 'claim coins' here. The system detected their bank data and awarded coins automatically. That's our core differentiator."

---

#### **Minute 1-2: Link Bank — Show Verification**

Navigate to **Link Bank** page.

**What to do:**
1. Select bank: **ICICI**
2. Enter account number: `9876543210`
3. Click "Link Account"
4. Show success message

**What to highlight:**
- "This simulates OAuth flow with the bank"
- "In production, this would fetch real transaction data"
- "System automatically analyzes linked account for verified behaviors"

**Optional:** Show the verified behaviors that were detected:
```bash
curl http://localhost:8000/api/bank/verify-behaviors/1
```

Shows:
- On-time payments detected
- Credit score changes tracked
- Direct deposits identified
- Coins automatically awarded

---

#### **Minute 2-3: Earn — Multiple Earning Paths**

Navigate to **Earn** page.

**What to highlight:**
```
9 Earning Actions Available:
✓ On-time Payment    (+500)  [Verified via bank]
✓ Credit Score ↑     (+400)  [Verified via bureau]
✓ Savings Milestone  (+350)  [User creates goal]
✓ Direct Deposit     (+200)  [Verified via bank]
✓ Learn Finance      (+150)  [Educational module]
⊙ Daily Check-in     (+50)   [Daily habit]
⊙ Watch Ad           (+10)   [Engagement]
⊙ Referral           (+300)  [Social growth]
⊙ Easter Egg         (+200)  [Hidden rewards]
```

**Claim a coin action:**
1. Click "Daily Check-in" → +50 coins
2. Show success toast: "You earned 50 coins!"
3. Check Dashboard → balance increased

**Key message:** "Three types of earning: bank-verified (100% real), user-verified (education/goals), and gamified (games/streaks). Users see the mix."

---

#### **Minute 3-4: Z-Kart — Commerce Loop**

Navigate to **Z-Kart** page.

**What to highlight:**
- Product grid: 8 products across categories (Food, Travel, Retail, Entertainment)
- Each product shows: base price, coin cost, discount %
- Example: "Starbucks Gift Card - ₹500 base, 250 coins, +10% coin discount"

**Buy a product:**
1. Select "Starbucks Gift Card" (costs 250 coins)
2. Click "Buy"
3. Show confirmation: "Successfully purchased!"
4. Check Dashboard → balance decreased by 250

**Key message:** "Coins have real purchasing power. Users don't just 'collect' them—they spend them. This closes the loop and prevents inflation."

---

#### **Minute 4-5: Games + Tier Progress**

Navigate to **Games** page.

**Play Scratch Card:**
1. Click "Play Scratch Card" (free)
2. Show random result (try_again / small_win / medium_win / jackpot)
3. If win, coins awarded
4. Try 2-3 times to show variance

**Back to Dashboard:**
1. Check updated balance
2. Check tier progress toward Gold
3. Show: "1,400 more coins needed, 2 more verified behaviors needed for Gold tier"

**Key message:** "Gamification keeps users engaged, but verified behaviors drive real progress toward tiers. Tiers are the long-term goal."

---

## Key Statistics to Share

| Metric | Value |
|--------|-------|
| **Initial Demo State** | 1,600 coins (no manual claims—all verified) |
| **Tier Progress** | Silver tier achieved after bank linking + 2 verified behaviors |
| **Earning Paths** | 9 different earning actions |
| **Commerce Options** | 8 Z-Kart products + games + flash deals + auctions + clubs |
| **Verification Methods** | Bank API + Credit Bureau + User Self-Report |
| **Data Logged** | Every action tracked to SQLite (audit trail) |
| **Database Tables** | 9 tables (users, behaviors, transactions, linked_accounts, products, purchases, credit_score_history, savings_goals, bank_transactions) |

---

## Common Demo Questions

**Q: Is the bank API real?**
A: For the hackathon MVP, it's a mock that returns simulated data (HDFC/ICICI/Axis banks with realistic transaction patterns). In production, we'd integrate with real bank APIs (Open Banking, OAuth flows).

**Q: Why are verified behaviors important?**
A: They solve the "free coin vending machine" problem. Users can't spam actions for coins—they earn by demonstrating real financial discipline (on-time payments, credit improvement, savings goals).

**Q: How do you prevent coin inflation?**
A: 5 spending sinks (Z-Kart, games, flash deals, auctions, clubs) absorb coins. Tier progression creates long-term goals. Daily caps prevent engagement-farming.

**Q: What's the business model?**
A: Take-rate on Z-Kart purchases (users save 5-10% with coins, we negotiate bulk discounts with brands). Data licensing (anonymized behavioral profiles). Lending (high credit score holders are creditworthy for loans).

**Q: How does this differentiate from CRED?**
A: CRED rewards bill payments. Zolve rewards **financial discipline metrics**—credit score, savings, payment consistency—verified via APIs. We're building a behavioral finance engine, not a payments app.

---

## Files to Reference During Demo

- **Database:** `zolve.db` (SQLite, 9 tables, full audit trail)
- **Backend API:** `http://localhost:8000` (19 endpoints, 4 route modules)
- **Frontend:** `http://localhost:8501` (9-page Streamlit app, CRED dark theme)
- **Code Structure:**
  ```
  backend/
  ├── main.py (FastAPI entry point)
  ├── routes/ (4 modularized route modules)
  ├── game_engine.py (business logic)
  ├── database.py (SQLite with dependency injection)
  ├── models.py (Pydantic validators)
  └── constants.py (50+ constants)
  
  frontend/
  └── app.py (Streamlit multi-page app, 9 pages)
  ```

---

## Post-Demo Talking Points

**Strengths to Emphasize:**
1. ✅ **Verified earning:** No fake coins claimed for free. Behaviors are proven via APIs.
2. ✅ **Real tier progression:** Silver/Gold tiers require both coins AND verified behaviors (prevents gaming the system).
3. ✅ **Commerce integration:** Z-Kart shows actual spending, not just collection.
4. ✅ **Data flywheel:** Every action logged. We can build behavioral profiles for credit/lending products.
5. ✅ **Production-ready code:** Modularized routes, exception hierarchy, Pydantic validators, type hints (CLAUDE.md standards).

**Roadmap to Highlight:**
- **Phase 2 (Post-Hackathon):** Real bank API integrations, multi-user Z-Clubs, price comparison engine, advanced earning triggers.
- **Phase 3:** Data analytics dashboard, credit score modeling, lending product.
- **Phase 4:** Cross-sell ML engine, referral network effects, platform scaling.

---

## Contingency Plans

**If Backend Fails:**
- Show screenshots of API responses (provided in repo)
- Explain architecture via system_design.md
- Play recorded demo video (if available)

**If Frontend Fails:**
- Use Postman/curl to demo endpoints
- Show database state via `sqlite3 zolve.db`
- Walk through code structure and design

**If Demo Time is Short:**
- Skip Flash Deals/Auctions/Clubs (UI-only, not core loop)
- Focus on: Dashboard → Link Bank → Earn → Z-Kart → Games → Tier Progress
- Emphasize verified earning system (the real differentiator)

---

## Success Metrics

Demo is successful if judges/stakeholders say:

1. **"I understand the core loop"** → behavior → coins → tier → spending → discipline
2. **"Verified earning is clever"** → solves fake claim problem
3. **"The code is clean"** → clear architecture, type-safe, modularized
4. **"This could scale"** → database design sound, API extensible, business model viable

---

## Technical Details (If Asked)

**Database Schema:**
```sql
users (id, name, email, coin_balance, tier, credit_score)
coin_transactions (user_id, amount, event_type, description)
behaviors (user_id, behavior_type, verified, verification_source)
linked_accounts (user_id, bank_name, account_number)
bank_transactions (account_id, transaction_date, description, amount, is_on_time)
products (id, name, category, base_price, coin_discount_pct)
purchases (user_id, product_id, coins_spent)
```

**API Endpoints (19 total):**
- `POST /api/coins/earn` — Earn coins for action
- `GET /api/coins/balance/{user_id}` — Check balance
- `POST /api/bank/link` — Link bank account
- `POST /api/bank/verify-behaviors/{user_id}` — Auto-detect behaviors
- `GET /api/zkart/products` — List products
- `POST /api/zkart/purchase` — Buy with coins
- `POST /api/games/scratch` — Play scratch card
- `POST /api/games/spin` — Play spin wheel
- Plus: dashboard, tier-progress, leaderboard, verified-behaviors, history endpoints

**Game Mechanics:**
- Scratch Card: 40% try_again, 35% small (50), 20% medium (150), 5% jackpot (500)
- Spin Wheel: 6 segments, rewards [50, 100, 200, 300, 500, 1000], costs 100 coins

---

**Good luck with the demo! You've built a solid MVP. Focus on telling the story of verified earning—that's your differentiation.** 🚀
