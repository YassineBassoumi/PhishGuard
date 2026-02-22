"""
PhishGuard AI - FastAPI Application
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analysis
from contextlib import asynccontextmanager
from app.middleware import rate_limit_middleware, DatabaseMonitorMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting PhishGuard AI...")
    
    # Import models to register them with Base
    from app.models import database_models, user_models, email_provider_models
    from app.database import init_db
    
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down PhishGuard AI...")


# Initialize FastAPI app
app = FastAPI(
    title="PhishGuard AI API",
    description="AI-powered phishing detection system for emails and URLs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Alternative Vite port
    "http://localhost:3000",  # React dev server (alternative)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add database monitoring middleware
app.add_middleware(DatabaseMonitorMiddleware)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(analysis.router, prefix="/api", tags=["API"])
from app.routes import gmail, outlook, auth, email_providers, admin, two_factor, sessions, password_reset, email_verification, security, notifications, profile
app.include_router(gmail.router, prefix="/api", tags=["Gmail"])
app.include_router(outlook.router, prefix="/api", tags=["Outlook"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(email_providers.router, prefix="/api/email", tags=["Email Providers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(two_factor.router, tags=["Two-Factor Authentication"])
app.include_router(sessions.router, tags=["Sessions"])
app.include_router(password_reset.router, tags=["Password Reset"])
app.include_router(email_verification.router, tags=["Email Verification"])
app.include_router(security.router, tags=["Security"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(profile.router, tags=["Profile"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to PhishGuard AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
