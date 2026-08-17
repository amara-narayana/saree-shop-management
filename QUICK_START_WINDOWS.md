# 🚀 Quick Start Guide - Saree Inventory System V2 (Windows)

## ⚡ One-Page Setup Instructions

### Step 1: Install Required Software

1. **Git**: Download from https://git-scm.com/download/win → Install with defaults
2. **Python 3.11+**: Download from https://python.org → ✅ CHECK "Add to PATH" during install
3. **PostgreSQL**: Download from https://postgresql.org/download → Use password `postgres`
4. **Node.js LTS**: Download from https://nodejs.org → Install with defaults

### Step 2: Create Database

Open "SQL Shell (psql)" from Start Menu, then type:
```sql
CREATE DATABASE saree_inventory_db;
\q
```

### Step 3: Setup Backend

Open Command Prompt or PowerShell:

```cmd
cd path\to\your\project\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file in `backend` folder:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saree_inventory_db
SECRET_KEY=supersecretkey_change_this_in_production_min_32_chars_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PAYMENT_PROVIDER=test
PAYMENT_MODE=test
```

Run migrations and start server:
```cmd
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at http://127.0.0.1:8000

### Step 4: Setup Frontend (New Terminal)

Open NEW Command Prompt window:

```cmd
cd path\to\your\project\frontend
npm install
```

Create `.env` file in `frontend` folder:
```ini
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Start frontend:
```cmd
npm run dev
```

✅ Frontend running at http://localhost:5173

### Step 5: Create Admin User & Login

1. Go to http://127.0.0.1:8000/docs
2. Find POST `/api/v1/auth/register`
3. Click "Try it out", enter:
   ```json
   {"username": "admin", "email": "admin@shop.com", "password": "admin123", "role": "ADMIN"}
   ```
4. Click Execute
5. Go to http://localhost:5173/login
6. Login with: `admin` / `admin123`

## 🎯 You're Done!

Explore these features:
- **Dashboard**: Business intelligence with inventory aging, dead stock, reorder alerts
- **Sarees**: Add/manage products
- **Inventory**: View stock levels, aging analysis, smart recommendations
- **POS**: Process sales with cart system

## 🔧 Common Issues

| Problem | Solution |
|---------|----------|
| `python` not recognized | Reinstall Python, check "Add to PATH" |
| Database connection error | Verify `.env` has correct password |
| `alembic` not found | Run `venv\Scripts\activate` first |
| Frontend blank page | Check backend is running on port 8000 |
| CORS errors | Make sure backend started before frontend |

## 📋 What's Included

✅ V2 Business Intelligence Features:
- Inventory Aging Analysis (0-30, 31-60, 61-90, 91-180, 180+ days)
- Dead Stock Detection (>90 days no sale)
- Smart Reorder Engine (ROP = Demand × Lead Time + Safety Stock)
- Profit Intelligence & Margin Calculations
- Customer RFM Segmentation (VIP/Loyal/New/At-Risk)
- Supplier Performance Scorecard
- Loyalty Program & Coupon Engine
- Expense Management
- Cash Register Sessions

## 📞 Need Help?

- API Docs: http://127.0.0.1:8000/docs
- Backend Logs: Check terminal running uvicorn
- Frontend Logs: Press F12 in browser → Console tab
