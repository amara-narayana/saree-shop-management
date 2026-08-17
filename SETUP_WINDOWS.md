# Complete Windows Setup Guide - Saree Inventory & Logistics Management System V2

This guide will walk you through setting up and running the complete Saree Retail ERP system on Windows 11 from scratch.

## Prerequisites Installation

### Step 1: Install Git

1. Download Git for Windows from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Verify installation:
   ```cmd
   git --version
   ```

### Step 2: Install Python 3.11+

1. Download Python from: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Click "Install Now"
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### Step 3: Install PostgreSQL

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer (use default port 5432)
3. Set a password for the `postgres` superuser (remember this!)
4. Keep all components selected (pgAdmin, Command Line Tools)
5. Verify by opening "SQL Shell (psql)" from Start Menu:
   - Server: localhost (press Enter)
   - Database: postgres (press Enter)
   - Port: 5432 (press Enter)
   - Username: postgres (press Enter)
   - Password: [your password]

### Step 4: Install Node.js

1. Download Node.js LTS from: https://nodejs.org/
2. Run installer with default settings
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

## Project Setup

### Step 5: Clone/Access the Project

If you have the project in a folder (e.g., `C:\Projects\saree-inventory`):

```cmd
cd C:\Projects\saree-inventory
```

Or if cloning from Git:
```cmd
cd C:\Projects
git clone <your-repo-url> saree-inventory
cd saree-inventory
```

### Step 6: Create PostgreSQL Database

1. Open "SQL Shell (psql)" from Start Menu
2. Connect as postgres user
3. Run:
   ```sql
   CREATE DATABASE saree_inventory_db;
   \q
   ```

## Backend Setup

### Step 7: Navigate to Backend Directory

```cmd
cd backend
```

### Step 8: Create Python Virtual Environment

```cmd
python -m venv venv
```

### Step 9: Activate Virtual Environment

**For PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**For Command Prompt (CMD):**
```cmd
venv\Scripts\activate.bat
```

You should see `(venv)` prefix in your terminal.

### Step 10: Install Python Dependencies

```cmd
pip install -r requirements.txt
```

This installs FastAPI, SQLAlchemy, Pydantic, and other required packages.

### Step 11: Create Environment Configuration File

Create a file named `.env` in the `backend` folder with this content:

```ini
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/saree_inventory_db
SECRET_KEY=supersecretkey_change_this_in_production_min_32_chars_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PAYMENT_PROVIDER=test
PAYMENT_MODE=test
PAYMENT_API_KEY=test_key
PAYMENT_API_SECRET=test_secret
PAYMENT_WEBHOOK_SECRET=test_webhook_secret
APP_NAME=Saree Inventory Management System
DEBUG=True
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

**Replace `YOUR_PASSWORD` with your actual PostgreSQL password.**

### Step 12: Run Database Migrations

```cmd
alembic upgrade head
```

This creates all database tables. You should see messages about migrations running.

### Step 13: Create Initial Admin User (Optional - Can do via API later)

You can create an admin user using the Swagger UI after starting the server, or use Python:

```cmd
python -c "from app.db.database import engine, Base; from app.core.security import create_password_hash; print('Database ready')"
```

### Step 14: Start Backend Server

```cmd
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend is now running at:
- **API**: http://127.0.0.1:8000
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

**Keep this terminal open!**

## Frontend Setup

### Step 15: Open New Terminal

Open a new Command Prompt or PowerShell window (keep backend running).

### Step 16: Navigate to Frontend Directory

```cmd
cd C:\Projects\saree-inventory\frontend
```

Or wherever your project is located.

### Step 17: Install Node Dependencies

```cmd
npm install
```

This may take a few minutes. It installs React, Vite, Tailwind CSS, etc.

### Step 18: Create Frontend Environment File

Create a file named `.env` in the `frontend` folder:

```ini
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### Step 19: Start Frontend Development Server

```cmd
npm run dev
```

The frontend is now running at:
- **Application**: http://localhost:5173

## Using the Application

### Step 20: Access the Application

1. Open your browser to: **http://localhost:5173**
2. You'll be redirected to the login page

### Step 21: Create First Admin User

Since there are no users yet, use Swagger to create one:

1. Go to: http://127.0.0.1:8000/docs
2. Find `POST /api/v1/auth/register`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "username": "admin",
     "email": "admin@sareeshop.com",
     "password": "admin123",
     "role": "ADMIN"
   }
   ```
5. Click "Execute"
6. You should get a success response

### Step 22: Login to the Application

1. Go back to http://localhost:5173/login
2. Enter credentials:
   - **Username**: admin
   - **Password**: admin123
3. Click Login

### Step 23: Explore Features

You now have access to:
- **Dashboard**: Business intelligence overview with inventory aging, dead stock alerts, reorder recommendations
- **Sarees**: Product management with advanced attributes
- **Inventory**: Stock tracking and management
- **POS**: Point of Sale system

## Troubleshooting

### Issue: "python is not recognized"
- Reinstall Python and ensure "Add to PATH" is checked
- Restart your terminal/computer after installation

### Issue: "Alembic command not found"
- Ensure virtual environment is activated: `.\venv\Scripts\activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: Database connection error
- Verify PostgreSQL is running (check Windows Services)
- Check DATABASE_URL in `.env` has correct password
- Ensure database `saree_inventory_db` exists

### Issue: "npm is not recognized"
- Reinstall Node.js
- Restart terminal after installation

### Issue: Frontend won't load
- Ensure backend is running on port 8000
- Check `.env` file has correct API URL
- Clear browser cache and reload

### Issue: CORS errors in browser console
- Backend must be running before frontend
- Check CORS_ORIGINS in backend `.env` includes frontend URL

## Creating Sample Data

After logging in, you can:

1. **Add Sarees**: Go to /sarees and create products
2. **Make Sales**: Use /pos to create sales transactions
3. **View Analytics**: Dashboard will show real-time intelligence

## Production Deployment Notes

For production deployment:

1. Change `SECRET_KEY` to a strong random value
2. Set `DEBUG=False`
3. Use production database credentials
4. Configure proper payment gateway credentials
5. Set up SSL/HTTPS
6. Use environment variables instead of `.env` files
7. Configure proper backup procedures

## Next Steps

1. Add your product catalog
2. Configure suppliers
3. Set up customers
4. Process test sales
5. Explore business intelligence features:
   - Inventory aging analysis
   - Dead stock detection
   - Smart reorder recommendations
   - Customer RFM segmentation
   - Profit analytics

## Support

For issues or questions:
- Check backend logs in the terminal running uvicorn
- Check frontend logs in browser DevTools (F12)
- Review API documentation at http://127.0.0.1:8000/docs
