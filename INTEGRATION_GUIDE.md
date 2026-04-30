# Backend & Frontend Integration Guide

## Overview

The Zolve system is divided into two main components:

- **Backend**: FastAPI server (port 8000) - Handles all business logic, database operations, and API endpoints
- **Frontend**: Streamlit app (port 8501) - User interface that communicates with the backend via REST API

## Architecture

```
Frontend (Streamlit)
    ↓ HTTP Requests
Backend API (FastAPI)
    ↓ Database Operations
SQLite Database
```

## Getting Started

### Option 1: Using the Startup Script (Recommended)

**Windows:**
```bash
start.bat
```

**macOS/Linux:**
```bash
bash start.sh
```

This will:
1. Start the backend server on `http://localhost:8000`
2. Start the frontend app on `http://localhost:8501`
3. Automatically open the Streamlit app in your browser

### Option 2: Manual Startup

**Terminal 1 - Start Backend:**
```bash
cd backend
python main.py
```

Backend will be running at: `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
streamlit run frontend/app.py
```

Frontend will be running at: `http://localhost:8501`

## API Endpoints

All endpoints are prefixed with `/api/`. The frontend calls these from `http://localhost:8000/api/...`

### User Management
- `GET /api/user/{user_id}` - Get user profile with activity feed
- `GET /api/verified-behaviors/{user_id}` - Get verified financial behaviors
- `GET /api/tier-progress/{user_id}` - Get tier progression data

### Coins
- `POST /api/coins/earn` - Earn coins for an action
- `GET /api/coins/balance/{user_id}` - Get user coin balance
- `GET /api/coins/history/{user_id}` - Get transaction history

### Marketplace
- `GET /api/zkart/products` - List all products
- `GET /api/zkart/products/{product_id}` - Get product details
- `POST /api/zkart/purchase` - Purchase a product with coins

### Games
- `POST /api/games/scratch` - Play scratch card game
- `POST /api/games/spin` - Play spin wheel game

### Bank Integration
- `POST /api/bank/link` - Link a bank account
- `GET /api/bank/transactions/{user_id}` - Get linked bank transactions
- `POST /api/bank/verify-behaviors/{user_id}` - Verify financial behaviors
- `GET /api/bank/credit-score/{user_id}` - Get credit score data

## Frontend to Backend Communication

The frontend communicates with the backend using the `requests` library:

```python
# GET request
response = requests.get(f"http://localhost:8000/api/user/1", timeout=5)

# POST request
response = requests.post(
    f"http://localhost:8000/api/coins/earn",
    json={"user_id": 1, "action_type": "daily_checkin"},
    timeout=5
)
```

### Error Handling

The frontend handles three types of API errors:

1. **Connection Errors**: Backend is not running
2. **HTTP Errors**: 4xx or 5xx responses
3. **Timeout Errors**: Backend takes too long to respond

All errors are displayed to the user via `st.error()`.

## CORS Configuration

The backend has CORS enabled to allow requests from the frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows the frontend (running on port 8501) to make requests to the backend (running on port 8000).

## Database

Both the backend and frontend use a shared SQLite database:

- Location: `backend/zolve.db`
- Initialized on first backend startup
- Contains user data, transactions, products, behaviors, etc.

## Debugging

### Check if Backend is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "service": "zolve-backend"}
```

### Check if Frontend is Running

```bash
curl http://localhost:8501
```

You should see HTML content.

### View Backend Logs

Check the terminal where you started the backend. You'll see:
- Request logs
- Error messages
- Database operations

### View Frontend Logs

Check the terminal where you started Streamlit. You'll see:
- Page loads
- Widget interactions
- Error messages

## Common Issues

### "Connection refused" error in frontend

**Cause**: Backend is not running

**Solution**:
1. Start the backend: `cd backend && python main.py`
2. Wait 2-3 seconds for it to initialize
3. Refresh the Streamlit app

### "ModuleNotFoundError" when starting backend

**Cause**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

### Streamlit fails to connect to backend

**Cause**: CORS not enabled or firewall blocking

**Solution**:
1. Ensure CORS middleware is added (see `backend/main.py`)
2. Check that backend is actually running: `curl http://localhost:8000/health`
3. Try accessing API directly: `curl http://localhost:8000/api/user/1`

### "Address already in use" error

**Cause**: Port 8000 or 8501 is already in use

**Solution**:
1. Find and kill the existing process
2. Or start on different ports:
   - Backend: `python main.py --port 8001`
   - Frontend: `streamlit run frontend/app.py --server.port 8502`

## Environment Variables

Optional configuration:

```bash
# Backend
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Frontend
API_BASE_URL=http://localhost:8000  # Set in frontend/app.py
```

## Testing the Integration

1. **Start both services**
2. **Open the frontend**: http://localhost:8501
3. **Try these actions**:
   - View Dashboard - Should show user data from API
   - Click "Claim" on an earn action - Should update balance
   - Buy a product - Should deduct coins
   - Play a game - Should show results and update balance

All actions should trigger API calls to the backend and update the database.

## Production Deployment

For production, you would:

1. Run backend on a real server (e.g., AWS, Heroku)
2. Update frontend to point to production API URL
3. Use proper database (PostgreSQL) instead of SQLite
4. Add authentication and authorization
5. Add proper error handling and logging
6. Enable HTTPS

Example production URL:
```python
API_BASE_URL = "https://api.zolve.com"
```

## Support

If integration issues persist:

1. Check both servers are running
2. Verify ports are correct
3. Check network connectivity
4. Review error messages in logs
5. Test API endpoints directly with `curl`
