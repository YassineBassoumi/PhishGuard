"""
Script to manually verify a user's email (for testing)
Usage: python scripts/verify_user.py <username>
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import sys

load_dotenv()


async def verify_user(username: str):
    """Manually verify a user's email"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    # Convert SQLAlchemy URL to asyncpg format
    connection_string = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(connection_string)
        
        # Find user
        user = await conn.fetchrow(
            "SELECT id, username, email, email_verified FROM users WHERE username = $1",
            username
        )
        
        if not user:
            print(f"❌ User '{username}' not found")
            await conn.close()
            return False
        
        if user['email_verified']:
            print(f"✓ User '{username}' is already verified")
            await conn.close()
            return True
        
        # Verify the user
        await conn.execute(
            "UPDATE users SET email_verified = true WHERE username = $1",
            username
        )
        
        print(f"✅ User '{username}' email verified successfully")
        print(f"   Email: {user['email']}")
        print(f"   User ID: {user['id']}")
        print(f"\nYou can now log in with this account!")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def main():
    """Main function"""
    print()
    print("=" * 70)
    print("Manual Email Verification Tool (for testing)")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_user.py <username>")
        print()
        return
    
    username = sys.argv[1]
    await verify_user(username)
    
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(main())
