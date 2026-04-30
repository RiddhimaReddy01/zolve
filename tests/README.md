# Zolve Backend Test Suite

Comprehensive testing suite for the Zolve MVP backend, simulating real user journeys: **earn coins → apply coin boost → checkout**.

## Overview

The test suite consists of two complementary testing approaches:

### 1. **User Journey Test Suite** (`test_user_journeys.py`)
- Simulates real end-to-end user flows
- Tests the **complete Z-Kart experience** with coin boosts
- Uses mock data from public sources and simulated bank/credit data
- Organized in 6 phases:
  1. Setup & Discovery (health checks, product discovery)
  2. Bank Linking & Verification (bank account integration)
  3. Coin Earning & Management (various earning methods)
  4. **Z-Kart Purchase with Coin Boost** (main feature test)
  5. Spending Sinks (flash deals, club deals, auctions)
  6. Summary & Reporting (final state verification)

### 2. **Integration Test Suite** (`test_integration.py`)
- Pytest-based integration tests
- Tests individual features and edge cases
- Validates data models and error handling
- Organized by feature area (coins, bank, marketplace, sinks, dashboard)

## Setup

### Prerequisites
- Python 3.8+
- Backend running on `http://localhost:8000`
- SQLite database initialized

### Installation

```bash
cd tests
pip install -r requirements.txt
```

## Running Tests

### Option 1: Full User Journey Test (Recommended for manual validation)

```bash
python test_user_journeys.py
```

**Output:**
- Comprehensive test report with 30+ test scenarios
- Real-time progress indicators
- Summary with pass/fail counts
- Sample API responses for debugging
- Journey-specific metrics (coins earned, products purchased, etc.)

### Option 2: Pytest Integration Tests (Recommended for CI/CD)

```bash
pytest test_integration.py -v
```

**Options:**
```bash
# Run with coverage
pytest test_integration.py --cov=.

# Run specific test class
pytest test_integration.py::TestZKartMarketplace -v

# Run single test
pytest test_integration.py::TestZKartMarketplace::test_purchase_product_valid -v

# Run with detailed output
pytest test_integration.py -vv
```

### Option 3: Both Test Suites

```bash
# Start backend first
cd backend && python main.py &

# Run both test suites
python test_user_journeys.py
pytest test_integration.py -v
```

## Test Coverage

### Phase 1: Setup & Discovery (4 tests)
- ✓ Health check
- ✓ User dashboard retrieval
- ✓ Product discovery
- ✓ Category listing

### Phase 2: Bank & Verification (4 tests)
- ✓ Bank account linking
- ✓ Bank transaction retrieval
- ✓ Financial behavior verification
- ✓ Credit score checking

### Phase 3: Coin Earning (3 tests)
- ✓ Daily check-in earnings
- ✓ Coin balance retrieval
- ✓ Transaction history

### Phase 4: Z-Kart Purchase with Coin Boost ⭐ (3 tests)
**Main feature test:**
- ✓ Browse products by category
- ✓ View product details with coin boost info
- ✓ **Purchase with coin discount applied**

Example:
```
Product: Starbucks Gift Card ₹500
Coins Required: 250
Coin Boost: 10% additional discount
Savings: ₹50
Total Price: ₹450 (₹500 - ₹50)
```

### Phase 5: Spending Sinks (5 tests)
- ✓ Flash deals discovery and redemption
- ✓ Club deals discovery and joining
- ✓ Auction browsing
- ✓ Spin wheel entries

### Phase 6: Summary & Reporting (3 tests)
- ✓ Tier progress tracking
- ✓ Verified behaviors summary
- ✓ Final balance verification

## Mock Data

### Products (Z-Kart)
- **120 synthetic products** across realistic categories
- Categories: Food, Retail, Travel, Entertainment, Fitness
- Brands: Starbucks, Amazon, Netflix, Decathlon, MakeMyTrip, etc.
- Base prices: ₹100 - ₹5000
- Coin boosts: 5-20% additional discount

### Bank Transactions
- **150 mock transactions** per linked account
- Transaction types: salary, payments, transfers, bills
- Realistic amounts and dates
- On-time/late payment detection

### Spending Sinks
- **Flash Deals**: High-value electronics with time-limited discounts
- **Club Deals**: Group purchasing (rental rewards, savings clubs)
- **Auctions**: Premium items with bidding simulation
- **Spin Wheel**: Gamified reward entries

## Key Features Tested

### Coin Economy
| Action | Coins |
|--------|-------|
| Daily Check-in | 50 |
| On-Time Payment | 500 |
| Credit Score Up | 400 |
| Savings Milestone | 350 |
| Referral | 300 |
| Education Module | 150 |
| Ad Watch | 10 |

### User Tiers
| Tier | Min Coins | Min Behaviors |
|------|-----------|---------------|
| Basic | 0 | 0 |
| Silver | 1,000 | 2 |
| Gold | 3,000 | 5 |

### Z-Kart Coin Boost
- Default: 5-10% additional discount when paying with coins
- Applied to product base price
- Combined with bank verification rewards
- Creates incentive for ecosystem engagement

## Expected Results

### Successful Journey Output:
```
[PHASE 1] Setup & Discovery
✓ PASS: Health Check
✓ PASS: Get User Dashboard - balance: 50 coins
✓ PASS: List Z-Kart Products - Found 120 products

[PHASE 2] Bank Linking & Verification
✓ PASS: Link Bank Account - Status: linked
✓ PASS: Get Bank Transactions - Retrieved 150 transactions
✓ PASS: Verify Behaviors - Verified 2 behaviors, awarded 900 coins

[PHASE 3] Coin Earning & Management
✓ PASS: Earn Coins (Daily Check-in) - Earned 50 coins
✓ PASS: Get Coin Balance - Total: 1050, Withdrawable: 900

[PHASE 4] Z-Kart Purchase with Coin Boost
✓ PASS: Get Product Details - Starbucks Gift Card ₹500, 10% boost
✓ PASS: Purchase with Coin Boost - Saved ₹50, new balance: 900

[PHASE 5] Spending Sinks
✓ PASS: List Flash Deals - Found 120 deals
✓ PASS: Redeem Flash Deal - Redeemed item, new balance: 700

[PHASE 6] Summary & Reporting
✓ PASS: Get Tier Progress - Silver tier, 60% progress to Gold
✓ PASS: Final Balance Check - balance: 700 coins

TEST SUMMARY
Total tests: 30
Passed: 30 ✓
Success rate: 100.0%
```

## Troubleshooting

### Backend Connection Error
```
✗ FAIL: Health Check
Error: Cannot connect to backend
```
**Solution:** Ensure backend is running on `http://localhost:8000`
```bash
cd backend
python main.py
```

### Insufficient Coins for Purchase
```
✗ FAIL: Purchase with Coin Boost
Error: Insufficient coins. Need 250, have 100
```
**Solution:** Run bank verification first to earn coins from behaviors
```
✓ PASS: Verify Behaviors - Verified 2 behaviors, awarded 900 coins
```

### Database Not Initialized
```
✗ FAIL: Get User Dashboard
Error: User not found
```
**Solution:** Backend initializes database on first run. Ensure no foreign key constraint violations.

## Adding New Tests

### For User Journey Tests
1. Add method to `TestSuite` class:
```python
def test_new_feature(self):
    """Test description."""
    try:
        resp = requests.get(f"{BASE_URL}/new-endpoint")
        self.log_result(
            "Feature Name",
            resp.status_code == 200,
            f"Description: {resp.json()}",
            resp.json() if resp.status_code != 200 else None,
        )
    except Exception as e:
        self.log_result("Feature Name", False, str(e))
```

2. Call in `run_all_tests()`:
```python
self.test_new_feature()
```

### For Pytest Integration Tests
1. Add test class or method:
```python
class TestNewFeature:
    """Test new feature."""
    
    def test_endpoint(self):
        """Test endpoint behavior."""
        resp = requests.get(f"{BASE_URL}/endpoint")
        assert resp.status_code == 200
        assert "field" in resp.json()
```

## Performance Expectations

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| Health Check | <100ms | Minimal load |
| Full User Journey | 5-10s | Includes DB operations |
| All Integration Tests | 15-20s | Parallel execution possible |
| Bank Verification | 100-200ms | Includes behavior detection |
| Z-Kart Purchase | 50-100ms | DB transaction |

## Real-World Validation

The test suite simulates real user behavior:
1. **Bank Integration**: Links HDFC/ICICI/Axis accounts
2. **Behavior Verification**: Detects on-time payments, credit improvements
3. **Coin Earning**: Tests all earning mechanisms
4. **Product Discovery**: Filters by category, checks pricing
5. **Purchase Flow**: Validates coin deduction and pricing
6. **Ecosystem Engagement**: Tests spending sinks for retention

## Notes

- Tests use **demo user ID 1** (Riddhima)
- Mock data is generated **deterministically** (same output each run)
- All prices/coins are fictional examples
- Bank data is simulated without real API calls
- Tests are **non-destructive** (read-heavy operations)
- Database state persists between test runs

## Support

For issues or questions:
1. Check test output for specific failure details
2. Review API response in failure logs
3. Verify backend is running and responding
4. Check database schema matches models
