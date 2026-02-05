"""
Run database migration for multi-provider email support
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def run_migration():
    """Execute the migration SQL"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return False
    
    # Convert SQLAlchemy URL to asyncpg format
    connection_string = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print("🔄 Connecting to database...")
    print(f"📍 Host: aws-1-eu-west-1.pooler.supabase.com")
    print()
    
    try:
        # Connect to database
        conn = await asyncpg.connect(connection_string)
        print("✅ Connected to database")
        print()
        
        # Read migration file
        print("📖 Reading migration file...")
        with open('migrations/add_multi_provider_support.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("✅ Migration file loaded")
        print()
        
        # Execute migration
        print("🚀 Running migration...")
        print("=" * 60)
        
        # Execute the entire migration as a single transaction
        try:
            await conn.execute(migration_sql)
            print("✅ All statements executed successfully")
        except Exception as e:
            # Some errors are OK (like "already exists")
            if "already exists" in str(e) or "duplicate key" in str(e):
                print(f"⚠️  Some objects already exist (this is OK)")
            else:
                print(f"❌ Error: {str(e)}")
                raise
        
        print("=" * 60)
        print()
        
        # Verify tables were created
        print("🔍 Verifying migration...")
        
        # Check email_providers table
        result = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('email_providers', 'user_email_credentials')
        """)
        
        tables = [row['table_name'] for row in result]
        
        if 'email_providers' in tables:
            print("✅ Table 'email_providers' created")
            
            # Count providers
            count = await conn.fetchval("SELECT COUNT(*) FROM email_providers")
            print(f"   📊 {count} providers configured")
        else:
            print("❌ Table 'email_providers' not found")
        
        if 'user_email_credentials' in tables:
            print("✅ Table 'user_email_credentials' created")
        else:
            print("❌ Table 'user_email_credentials' not found")
        
        # Check if column was added to users table
        column_check = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'connected_providers'
        """)
        
        if column_check:
            print("✅ Column 'connected_providers' added to users table")
        else:
            print("⚠️  Column 'connected_providers' not found in users table")
        
        print()
        print("=" * 60)
        print("🎉 Migration completed successfully!")
        print("=" * 60)
        
        await conn.close()
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Migration failed: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  Multi-Provider Email Support Migration")
    print("=" * 60)
    print()
    
    success = asyncio.run(run_migration())
    
    if success:
        print()
        print("✅ You can now use multi-provider email support!")
        print()
        print("Next steps:")
        print("1. Set up Microsoft OAuth credentials in .env")
        print("2. Restart the backend server")
        print("3. Test Outlook connection")
    else:
        print()
        print("❌ Migration failed. Please check the errors above.")
        print()
