"""
Database Monitoring Middleware
Monitors database health and sends alerts on failures
"""

import logging
import traceback
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import OperationalError, DatabaseError
import asyncio

logger = logging.getLogger(__name__)


class DatabaseMonitorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor database health and send alerts on failures
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.last_alert_time = None
        self.alert_cooldown = 300  # 5 minutes cooldown between alerts
        self.error_count = 0
        self.max_errors_before_alert = 3  # Send alert after 3 consecutive errors
    
    async def dispatch(self, request: Request, call_next):
        """
        Monitor database operations and catch connection errors
        """
        try:
            response = await call_next(request)
            
            # Reset error count on successful request
            if response.status_code < 500:
                self.error_count = 0
            
            return response
            
        except (OperationalError, DatabaseError) as e:
            # Database connection error detected
            self.error_count += 1
            
            logger.error(
                f"Database error on {request.method} {request.url.path}: {str(e)}",
                exc_info=True
            )
            
            # Send alert if threshold reached and cooldown expired
            if self.error_count >= self.max_errors_before_alert:
                await self._send_database_error_alert(e, request)
                self.error_count = 0  # Reset after sending alert
            
            # Return 503 Service Unavailable
            return Response(
                content='{"detail": "Database connection error. Please try again later."}',
                status_code=503,
                media_type="application/json"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise
    
    async def _send_database_error_alert(self, error: Exception, request: Request):
        """
        Send alert to admins about database error
        """
        try:
            # Check cooldown
            current_time = datetime.utcnow()
            if self.last_alert_time:
                time_since_last_alert = (current_time - self.last_alert_time).total_seconds()
                if time_since_last_alert < self.alert_cooldown:
                    logger.info(f"Skipping alert due to cooldown ({time_since_last_alert}s < {self.alert_cooldown}s)")
                    return
            
            # Import here to avoid circular dependency
            from app.services.notification_service import notification_service
            
            # Prepare error details
            error_details = {
                'error_message': str(error),
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'operation': f"{request.method} {request.url.path}",
                'traceback': traceback.format_exc()
            }
            
            # Send alert asynchronously (don't block the request)
            asyncio.create_task(
                notification_service.send_database_error_alert(error_details)
            )
            
            # Update last alert time
            self.last_alert_time = current_time
            
            logger.info("Database error alert sent to administrators")
            
        except Exception as e:
            logger.error(f"Failed to send database error alert: {str(e)}", exc_info=True)
