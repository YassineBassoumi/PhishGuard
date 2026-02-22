"""
Script to promote a user to SuperAdmin role
Usage: python scripts/promote_to_superadmin.py <username>
"""

import asyncio
import asyncpg
from dotenv import load_dotenv
import os
import sys

load_dotenv()


async def promote_user(username: str):
    """Promote a user to SuperAdmin"""
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
            "SELECT id, username, email, role FROM users WHERE username = $1",
            username
        )
        
        if not user:
            print(f"❌ User '{username}' not found")
            await conn.close()
            return False
        
        old_role = user['role']
        
        # Update user role
        await conn.execute(
            "UPDATE users SET role = 'SUPERADMIN'::userrole WHERE username = $1",
            username
        )
        
        print(f"✅ User '{username}' promoted from {old_role} to SUPERADMIN")
        print(f"   Email: {user['email']}")
        print(f"   User ID: {user['id']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def list_users():
    """List all users"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    # Convert SQLAlchemy URL to asyncpg format
    connection_string = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(connection_string)
        
        users = await conn.fetch(
            "SELECT username, email, role FROM users ORDER BY role DESC, username"
        )
        
        if not users:
            print("No users found in database")
            await conn.close()
            return
        
        print("\nExisting users:")
        print("-" * 70)
        for user in users:
            role_icon = "👑" if user['role'] == 'SUPERADMIN' else "🔧" if user['role'] == 'ADMIN' else "👤"
            print(f"  {role_icon} {user['username']:20} | {user['email']:30} | {user['role']}")
        print("-" * 70)
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    """Main function"""
    print()
    print("=" * 70)
    print("SuperAdmin User Promotion Tool")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/promote_to_superadmin.py <username>")
        await list_users()
        print()
        return
    
    username = sys.argv[1]
    success = await promote_user(username)
    
    if success:
        print()
        print("✅ Promotion successful!")
        print()
        print("Next steps:")
        print("1. Login with this user at http://localhost:8000/docs")
        print("2. Click 'Authorize' and enter credentials")
        print("3. Test the admin endpoints under 'Admin' section")
        print()
    
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(main())
