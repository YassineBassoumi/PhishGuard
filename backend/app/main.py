"""
PhishGuard AI - FastAPI Application
Main application entry point
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
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


async def _expired_sessions_cleanup_loop(interval_seconds: int = 6 * 3600):
    """
    Periodically delete rows from `user_sessions` whose `expires_at` is in the
    past. Runs forever until the task is cancelled at shutdown.
    """
    import asyncio
    from app.database import AsyncSessionLocal
    from app.services.session_service import session_service

    while True:
        try:
            async with AsyncSessionLocal() as db:
                deleted = await session_service.cleanup_expired_sessions(db)
                await db.commit()
                if deleted:
                    logger.info(f"Expired session cleanup: removed {deleted} row(s)")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning(f"Expired session cleanup failed: {e}")

        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            raise


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

    # Schedule periodic cleanup of expired user_sessions rows
    import asyncio
    cleanup_task = asyncio.create_task(_expired_sessions_cleanup_loop())
    logger.info("Expired session cleanup task scheduled (every 6h)")

    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down PhishGuard AI...")
        cleanup_task.cancel()
        try:
            await cleanup_task
        except (asyncio.CancelledError, Exception):
            pass


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

# Add validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    logger.error(f"Validation error on {request.method} {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )

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
