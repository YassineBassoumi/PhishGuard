"""
Initialize database tables
Run this once to create all tables
"""
import asyncio
from app.database import init_db, engine
from app.models import database_models, user_models, email_provider_models


async def main():
    """Initialize database"""
    print("=" * 60)
    print("Initializing PhishGuard Database")
    print("=" * 60)
    print()
    
    try:
        print("Creating tables...")
        await init_db()
        print("✅ Database tables created successfully!")
        print()
        print("Tables created:")
        print("  - users")
        print("  - analysis_history")
        print("  - statistics")
        print("  - email_providers")
        print("  - user_email_credentials")
        print()
        print("=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
