"""
PhishGuard Backend - Main Entry Point
Run this file to start the FastAPI server
"""
import uvicorn
import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class EndpointFilter(logging.Filter):
    """Filter out health check and notification polling endpoints from logs"""
    def filter(self, record: logging.LogRecord) -> bool:
        # Filter out GET requests to notification endpoints (they're just polling)
        message = record.getMessage()
        return not (
            'GET /api/notifications/recent' in message or
            'GET /api/health' in message
        )


def main():
    """Start the FastAPI server"""
    print("=" * 60)
    print("Starting PhishGuard Backend Server")
    print("=" * 60)
    print()
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/api/health")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Add filter to uvicorn access logger to reduce noise
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
