"""
Cleanup orphaned profile pictures
Removes image files that are not referenced in the database
"""
import sys
import os
import asyncio
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import async_session
from app.models.user_models import User

UPLOAD_DIR = Path("uploads/profile_pictures")

async def cleanup_orphaned_pictures():
    """Remove profile pictures that are not referenced in database"""
    
    if not UPLOAD_DIR.exists():
        print("✓ Upload directory doesn't exist, nothing to clean")
        return
    
    # Get all filenames from database
    async with async_session() as session:
        result = await session.execute(
            select(User.profile_picture).where(User.profile_picture.isnot(None))
        )
        db_filenames = {row[0] for row in result.fetchall()}
    
    print(f"📊 Found {len(db_filenames)} profile pictures in database")
    
    # Get all files in upload directory
    all_files = list(UPLOAD_DIR.glob("*"))
    print(f"📁 Found {len(all_files)} files in upload directory")
    
    # Find orphaned files
    orphaned = []
    for file_path in all_files:
        if file_path.is_file() and file_path.name not in db_filenames:
            orphaned.append(file_path)
    
    if not orphaned:
        print("✓ No orphaned files found!")
        return
    
    print(f"\n⚠️  Found {len(orphaned)} orphaned files:")
    for file_path in orphaned:
        size_kb = file_path.stat().st_size / 1024
        print(f"  - {file_path.name} ({size_kb:.1f} KB)")
    
    # Ask for confirmation
    response = input("\n❓ Delete these files? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    # Delete orphaned files
    deleted_count = 0
    total_size = 0
    for file_path in orphaned:
        try:
            size = file_path.stat().st_size
            file_path.unlink()
            deleted_count += 1
            total_size += size
            print(f"✓ Deleted: {file_path.name}")
        except Exception as e:
            print(f"✗ Failed to delete {file_path.name}: {e}")
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted: {deleted_count} files")
    print(f"   Freed: {total_size_mb:.2f} MB")

if __name__ == "__main__":
    print("🧹 Profile Picture Cleanup Tool")
    print("=" * 50)
    asyncio.run(cleanup_orphaned_pictures())
