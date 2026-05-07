# PhishGuard Backend

FastAPI backend for PhishGuard phishing detection system.

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic services
│   ├── utils/           # Utility functions
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application entry point
├── ml_models/           # Machine learning model files (.pkl)
├── scripts/             # Utility scripts
│   └── init_db.py       # Initialize database tables
├── .env                 # Environment variables (not in git)
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── run.py               # Main entry point to start server
└── README.md            # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with:
```env
DATABASE_URL=postgresql+asyncpg://[your-database-url]
SECRET_KEY=[your-jwt-secret-key]
GOOGLE_CLIENT_ID=[your-google-oauth-client-id]
GOOGLE_CLIENT_SECRET=[your-google-oauth-client-secret]
MICROSOFT_CLIENT_ID=[your-microsoft-oauth-client-id]
MICROSOFT_CLIENT_SECRET=[your-microsoft-oauth-client-secret]
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

### 4. Start Server

```bash
# Simple way
python run.py

# Or using uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## Available Scripts

### Database Management
```bash
# Initialize database tables
python scripts/init_db.py

# Train email phishing model
python scripts/train_email_model.py
```

## Features

- ✅ User authentication (JWT)
- ✅ Message/text phishing detection (ML-powered, SMS-trained model)
- ✅ URL phishing detection (100% accuracy)
- ✅ Gmail OAuth integration
- ✅ Outlook OAuth integration
- ✅ Bulk message analysis
- ✅ Analysis history tracking
- ✅ User statistics

**Note**: The email/message analysis uses an ML model trained on SMS spam data. It analyzes plain text content and does not require structured email headers (from, subject, etc.). See `scripts/train_email_model.py` for training details.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy (async)
- **ML**: scikit-learn, XGBoost
- **Auth**: JWT, OAuth2
- **Email APIs**: Gmail API, Microsoft Graph API

## Development

### Code Structure
- `app/models/` - Database models and schemas
- `app/routes/` - API endpoints
- `app/services/` - Business logic and ML models
- `ml_models/` - Trained ML model files

## Production Deployment

1. Set `reload=False` in `run.py`
2. Use a production WSGI server (gunicorn + uvicorn workers)
3. Set strong `SECRET_KEY` in environment
4. Enable HTTPS
5. Configure proper CORS origins
6. Set up database backups

## Support

For issues or questions, check the main project README.
