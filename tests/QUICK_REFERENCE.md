# Test Suite Quick Reference

## Run Tests

```bash
# Full user journey (recommended for manual testing)
python test_user_journeys.py

# Pytest integration tests
pytest test_integration.py -v

# Both
python test_user_journeys.py && pytest test_integration.py -v
```

## Test Files

| File | Purpose | Count | Runtime |
|------|---------|-------|---------|
| `test_user_journeys.py` | End-to-end journey simulation | 30 tests | 8-12s |
| `test_integration.py` | Pytest integration tests | 50+ tests | 15-20s |
| `conftest.py` | Pytest fixtures & config | - | - |

## Test Phases

| Phase | Tests | Duration |
|-------|-------|----------|
| Setup & Discovery | 4 | ~1s |
| Bank & Verification | 4 | ~1s |
| Coin Earning | 3 | ~1s |
| Z-Kart Purchase | 3 | ~1s |
| Spending Sinks | 5 | ~2s |
| Summary & Reporting | 3 | ~1s |

## Key Features Tested

### Coin Earning
- Daily check-in (50 coins)
- On-time payment (500 coins)
- Credit score improvement (400 coins)
- Savings milestone (350 coins)

### Z-Kart Marketplace
- Browse 120 products
- Filter by category
- View product details
- **Purchase with 5-10% coin boost**
- Apply discount to price

### Spending Sinks
- Flash deals (electronics, food)
- Club deals (group purchasing)
- Auctions (premium items)
- Spin wheel (gamified entries)

### Bank Integration
- Link HDFC/ICICI/Axis accounts
- Fetch 150 mock transactions
- Verify financial behaviors
- Check credit score

### User Management
- Dashboard with full profile
- Tier progression (Basic → Silver → Gold)
- Transaction history
- Leaderboard

## Mock Data

### Products (Z-Kart)
- **Count**: 120 synthetic products
- **Categories**: Food, Retail, Travel, Entertainment, Fitness
- **Brands**: Starbucks, Amazon, Netflix, Decathlon, Uber, MakeMyTrip, Flipkart, etc.
- **Price Range**: ₹100-₹5000
- **Coin Boost**: 5-20% additional discount

### Bank Transactions
- **Per Account**: 150 mock transactions
- **Types**: Salary, payments, transfers, bills
- **Date Range**: Monthly data
- **Status**: On-time/late detection

### Spending Items
- **Flash Deals**: 120 items with countdown
- **Club Deals**: 120 group purchasing options
- **Auctions**: 120 premium items with bids
- **Spin Wheel**: 120 gamified entries

## Pytest Commands

```bash
# Run all tests
pytest test_integration.py -v

# Run specific class
pytest test_integration.py::TestZKartMarketplace -v

# Run specific test
pytest test_integration.py::TestZKartMarketplace::test_purchase_product_valid -v

# Run with markers
pytest test_integration.py -m marketplace -v
pytest test_integration.py -m "bank or coins" -v

# Show coverage
pytest test_integration.py --cov=. --cov-report=html

# Stop on first failure
pytest test_integration.py -x

# Show print statements
pytest test_integration.py -v -s
```

## API Endpoints Covered

| Endpoint | Method | Tests |
|----------|--------|-------|
| `/health` | GET | Health |
| `/api/user/{id}` | GET | Dashboard |
| `/api/coins/balance/{id}` | GET | Balance |
| `/api/coins/earn` | POST | Earning |
| `/api/coins/history/{id}` | GET | History |
| `/api/bank/link` | POST | Bank Linking |
| `/api/bank/transactions/{id}` | GET | Bank Transactions |
| `/api/bank/verify-behaviors/{id}` | POST | Verification |
| `/api/bank/credit-score/{id}` | GET | Credit Score |
| `/api/zkart/products` | GET | Product List |
| `/api/zkart/products/{id}` | GET | Product Details |
| `/api/zkart/purchase` | POST | Purchase |
| `/api/spending/{sink}` | GET | Spending Items |
| `/api/spending/{sink}/redeem` | POST | Redemption |
| `/api/tier-progress/{id}` | GET | Tier Progress |
| `/api/verified-behaviors/{id}` | GET | Behaviors |
| `/api/leaderboard` | GET | Leaderboard |

## Typical Journey Flow

```
1. Health Check ✓
2. Get Dashboard ✓
3. List Products ✓
4. Link Bank Account ✓
5. Get Bank Transactions ✓
6. Verify Behaviors → Award Coins ✓
7. Check Balance ✓
8. Browse Products ✓
9. Purchase with Coins ✓
10. Redeem Spending Sink ✓
11. Check Final Balance ✓
```

## Expected Results

### Success
```
✓ PASS: Purchase with Coin Boost
  Purchased: Starbucks Gift Card
  Coins spent: 250
  Discount: ₹50 (10%)
  New balance: 750
```

### Expected Failure (Normal)
```
✗ FAIL: Purchase with Coin Boost
  Insufficient coins. Need 250, have 50
  → Solution: Run bank verification first
```

### System Failure (Investigate)
```
✗ FAIL: Get Product Details
  Failed with status 500
  → Solution: Check backend logs
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` | Start backend: `python backend/main.py` |
| `User not found` | Delete DB: `rm zolve.db` and restart backend |
| `Insufficient coins` | Run bank verification or earn coins first |
| `Database locked` | Restart backend to reset connections |

## Test Markers (Pytest)

```bash
pytest test_integration.py -m integration          # Integration tests
pytest test_integration.py -m bank                 # Bank tests
pytest test_integration.py -m marketplace          # Z-Kart tests
pytest test_integration.py -m coins                # Coin tests
pytest test_integration.py -m sinks                # Spending sinks
pytest test_integration.py -m "not slow"           # Exclude slow tests
```

## Configuration

### `pytest.ini`
- Discovery patterns: `test_*.py`
- Min version: Python 3.8
- Timeout: 30 seconds per test
- Output: Verbose with short traceback

### `conftest.py`
- Auto-waits for backend (30 retries, 1s each)
- Fixtures: `api_base_url`, `test_user_id`

### `requirements.txt`
- pytest 7.4.3
- requests 2.31.0
- pytest-cov 4.1.0

## Performance Baseline

| Operation | Time |
|-----------|------|
| Health check | <100ms |
| Get balance | 50ms |
| Earn coins | 100ms |
| Bank verify | 200-300ms |
| List products | 100ms |
| Purchase | 100-150ms |
| Full journey (30 tests) | 8-12s |

## Data Constants

| Item | Value |
|------|-------|
| Demo User ID | 1 |
| Demo User | Riddhima |
| Demo Email | riddhima@zolve.app |
| Banks | HDFC, ICICI, Axis |
| Products | 120 |
| Categories | 8 |
| Bank Transactions | 150 |
| Spending Items | 600 (120 × 5) |

## Common Test Patterns

### Assert Status Code
```python
assert resp.status_code == 200
```

### Assert Response Fields
```python
assert "balance" in resp.json()
assert resp.json()["user_id"] == 1
```

### Assert List Length
```python
products = resp.json()
assert len(products) > 0
```

### Handle Either/Or
```python
assert resp.status_code in [200, 400]  # Success or expected error
```

## Notes

- All tests use **demo user ID 1**
- Database state **persists** between runs
- Tests are **non-destructive** (mostly read operations)
- Mock data is **deterministic** (same output each run)
- No real bank/credit APIs called
- All prices/coins are **fictional examples**

---

**See `README.md` for detailed documentation and `../TESTING.md` for complete guide.**
