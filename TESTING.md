# Zolve Backend Testing Guide

Complete guide to testing the Zolve MVP backend with **real user journey simulation**.

## Quick Start

### 1️⃣ Start the Backend
```bash
cd backend
python main.py
```

Backend will start on `http://localhost:8000`

### 2️⃣ Install Test Dependencies
```bash
cd tests
pip install -r requirements.txt
```

### 3️⃣ Run Tests

#### Option A: Full User Journey Test (Manual Validation)
```bash
python test_user_journeys.py
```
- 30+ test scenarios covering complete user flow
- Real-time progress with ✓/✗ indicators
- Detailed summary with metrics
- Best for: Manual testing, feature validation, demo purposes

#### Option B: Pytest Integration Tests (Automated)
```bash
pytest test_integration.py -v
```
- Organized by feature area
- Easy to run in CI/CD pipelines
- Better for: Continuous integration, regression testing

#### Option C: Both Tests
```bash
python test_user_journeys.py && pytest test_integration.py -v
```

## What Gets Tested

### 🏦 Bank Integration
```
Link Bank Account (HDFC/ICICI/Axis)
  ↓
Fetch Bank Transactions (150 mock transactions)
  ↓
Verify Financial Behaviors (on-time payment, credit improvement)
  ↓
Award Withdrawable Coins
```

### 💰 Coin Economy
```
Earn Coins From:
  - Daily Check-in (50 coins/day)
  - On-Time Payments (500 coins)
  - Credit Score Improvement (400 coins)
  - Savings Milestones (350 coins)
  - Referrals (300 coins)
  - Education Modules (150 coins)
  - Ad Watches (10 coins)

Manage Coins:
  - Check Total Balance
  - Check Withdrawable Balance
  - View Transaction History
  - Track Tier Progress (Basic → Silver → Gold)
```

### 🛒 Z-Kart Marketplace (Core Feature)
```
Browse Products
  - All 120 products across 8+ categories
  - Filter by: Food, Travel, Retail, Entertainment, Fitness
  - Real brands: Starbucks, Amazon, Netflix, Decathlon, MakeMyTrip

Apply Coin Boost
  - Base discount: 5-10% with coins
  - Additional savings: ₹25-500 per purchase
  - Example:
    * Product: Starbucks Gift Card ₹500
    * Base price: ₹500
    * Coin boost: 10% = ₹50 savings
    * Price with coins: ₹450

Purchase with Coins
  - Deduct coins from balance
  - Record purchase in history
  - Verify new balance
```

### 🎁 Spending Sinks (Ecosystem Engagement)
```
Flash Deals
  - Electronics, food, travel items
  - Time-limited offers (15+ minutes)
  - 25-60% discounts
  
Club Deals
  - Group purchasing (5-85 members)
  - Housing, savings, credit building clubs
  - Shared pool pricing
  
Auctions
  - Premium items (iPhone, MacBook, trips)
  - Competitive bidding (3-35 bids)
  - High coin cost (450-2200 coins)

Spin Wheel
  - Gamified entries (100-500 coins)
  - Rewards: 50-1000 coins
```

## Test Organization

### Phase 1: Setup & Discovery
- Health check
- User dashboard
- Product listing
- Category discovery

### Phase 2: Bank & Verification
- Link bank account
- Fetch transactions
- Verify behaviors
- Check credit score

### Phase 3: Coin Earning
- Daily check-in
- Check balance
- Transaction history

### Phase 4: Z-Kart Purchase ⭐
- Browse by category
- View product details
- **Purchase with coin boost** (main feature)

### Phase 5: Spending Sinks
- Flash deals
- Club deals
- Auctions
- Spin wheel

### Phase 6: Summary
- Tier progress
- Verified behaviors
- Final balance

## Mock Data Samples

### Products (Z-Kart)
```json
{
  "id": 1,
  "name": "Starbucks Gift Card #1",
  "category": "Food",
  "base_price": 500.00,
  "coin_discount_pct": 10,
  "coins_required": 250,
  "stock": 50
}
```

### Bank Transactions
```json
{
  "date": "2026-04-15",
  "description": "Monthly Salary Deposit",
  "amount": 78000,
  "due_date": null,
  "is_on_time": true,
  "status": "completed"
}
```

### Spending Sinks
```json
{
  "id": 1,
  "title": "Premium Headphones #1",
  "sink_type": "flash-deals",
  "category": "Electronics",
  "coin_cost": 1500,
  "original_price": 4999,
  "discount_pct": 35,
  "final_price": 3249.35,
  "available": true,
  "expires_at": "2026-04-30T10:15:00"
}
```

## Test Results Interpretation

### Successful Run
```
✓ PASS: Health Check
✓ PASS: Get User Dashboard - User: Riddhima, Initial balance: 50 coins
✓ PASS: List Z-Kart Products - Found 120 products across categories
✓ PASS: List Flash Deals - Found 120 flash deals
```

### Expected Failures (Normal)
```
✗ FAIL: Purchase with Coin Boost
  Insufficient coins. Need 250, have 100
```
**Why?** This is expected if bank verification hasn't awarded coins yet.
**Solution:** Run `Verify Behaviors` first or `Earn Coins` from daily check-in.

### Actual Failures (Investigate)
```
✗ FAIL: Get Product Details
  Failed with status 500
```
**Why?** Backend error
**Solution:** Check backend logs for exceptions, verify database initialization

## Performance Expectations

| Test | Time | Notes |
|------|------|-------|
| Health Check | <100ms | Quick connectivity test |
| Coin Earning | 50-100ms | Database write |
| Bank Verification | 200-300ms | Multiple transaction checks |
| Z-Kart Purchase | 100-150ms | Inventory + coin deduction |
| Full Journey (30 tests) | 8-12s | Total end-to-end |
| Pytest Suite (50 tests) | 20-30s | Parallel execution |

## Pytest Advanced Usage

### Run Specific Test Class
```bash
pytest test_integration.py::TestZKartMarketplace -v
```

### Run Specific Test
```bash
pytest test_integration.py::TestZKartMarketplace::test_purchase_product_valid -v
```

### Run with Coverage
```bash
pytest test_integration.py --cov=. --cov-report=html
```

### Run Only Tests with Marker
```bash
pytest test_integration.py -m marketplace -v
pytest test_integration.py -m "bank or coins" -v
```

### Run Tests Excluding Slow Tests
```bash
pytest test_integration.py -m "not slow" -v
```

### Verbose Output with Full Traceback
```bash
pytest test_integration.py -vv --tb=long
```

### Stop on First Failure
```bash
pytest test_integration.py -x
```

### Show Print Output
```bash
pytest test_integration.py -v -s
```

## Troubleshooting

### Backend Not Responding
```
✗ FAIL: Health Check
  Cannot connect to backend: Connection refused
```
**Steps:**
1. Check if backend is running: `python backend/main.py`
2. Verify it's on port 8000: `curl http://localhost:8000/health`
3. Check for port conflicts: `lsof -i :8000` (macOS/Linux)

### Database Errors
```
✗ FAIL: Get User Dashboard
  User not found
```
**Steps:**
1. Delete database: `rm zolve.db`
2. Restart backend (it auto-initializes)
3. Re-run tests

### Insufficient Coins
```
✗ FAIL: Purchase with Coin Boost
  Insufficient coins. Need 250, have 50
```
**Steps:**
1. Run bank verification first: `test_verify_behaviors()`
2. Or earn coins: `test_earn_coins_action()`
3. Or check tier progress: `test_get_tier_progress()`

### Rate Limiting or Daily Cap
```
✗ FAIL: Earn Coins (Daily Check-in)
  Daily earning cap exceeded
```
**Steps:**
1. This is expected behavior (anti-spam)
2. Try different action type: `credit_score_up`, `education_module`
3. Or test next day

## Customizing Tests

### Add New Test to User Journey Suite
Edit `tests/test_user_journeys.py`:
```python
def test_my_feature(self):
    """Test my new feature."""
    try:
        resp = requests.get(f"{BASE_URL}/my-endpoint")
        self.log_result(
            "My Feature",
            resp.status_code == 200,
            f"Success message",
            resp.json() if resp.status_code != 200 else None,
        )
    except Exception as e:
        self.log_result("My Feature", False, str(e))

# Add to run_all_tests()
self.test_my_feature()
```

### Add New Pytest Test
Edit `tests/test_integration.py`:
```python
class TestMyFeature:
    """Test my feature."""
    
    def test_endpoint(self):
        """Test endpoint behavior."""
        resp = requests.get(f"{BASE_URL}/my-endpoint")
        assert resp.status_code == 200
        data = resp.json()
        assert "field" in data
```

## Test Data Reference

### Constants Used
- **Demo User ID**: 1 (Riddhima)
- **Demo User Email**: riddhima@zolve.app
- **Banks**: HDFC, ICICI, Axis
- **Tiers**: Basic (0 coins), Silver (1000+ coins), Gold (3000+ coins)
- **Products**: 120 across 8 categories
- **Spending Items**: 120 per sink type × 5 types = 600 items

### API Endpoints Tested
```
GET  /health                            # Health check
GET  /api/user/{user_id}                # User dashboard
GET  /api/coins/balance/{user_id}       # Coin balance
POST /api/coins/earn                    # Earn coins
GET  /api/coins/history/{user_id}       # Transaction history
POST /api/bank/link                     # Link bank account
GET  /api/bank/transactions/{user_id}   # Bank transactions
POST /api/bank/verify-behaviors/{user_id}  # Verify behaviors
GET  /api/bank/credit-score/{user_id}   # Credit score
GET  /api/zkart/products                # List products
GET  /api/zkart/products/{product_id}   # Product details
POST /api/zkart/purchase                # Purchase product
GET  /api/spending/{sink_type}          # List spending items
POST /api/spending/{sink_type}/redeem   # Redeem item
GET  /api/tier-progress/{user_id}       # Tier progress
GET  /api/verified-behaviors/{user_id}  # Verified behaviors
GET  /api/leaderboard                   # Leaderboard
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Backend Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r tests/requirements.txt
      - name: Start backend
        run: python backend/main.py &
      - name: Wait for backend
        run: sleep 5
      - name: Run tests
        run: pytest tests/test_integration.py -v --tb=short
```

## Best Practices

1. **Run both test suites**: User journey for validation, pytest for CI/CD
2. **Test in isolation**: Don't depend on test execution order
3. **Use consistent user ID**: Simplifies debugging
4. **Clean database between full runs**: `rm zolve.db` before comprehensive testing
5. **Check logs**: Backend logs help identify issues
6. **Document failures**: Note what failed and why for debugging

## Support

For issues:
1. Check `tests/README.md` for detailed documentation
2. Review backend logs: `backend/main.py` output
3. Verify database: `sqlite3 zolve.db ".tables"`
4. Test connectivity: `curl http://localhost:8000/health`

---

**Happy testing! 🚀**
