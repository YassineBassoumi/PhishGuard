"""
PhishGuard Backend - Main Entry Point
Run this file to start the FastAPI server
"""
import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
