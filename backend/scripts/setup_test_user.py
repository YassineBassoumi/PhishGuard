"""
Create or reset a test user for the deactivation/reactivation E2E test.

  - If the user does not exist, creates it.
  - Sets: email_verified=True, is_active=True, is_banned=False, two_factor_enabled=False.
  - Resets the password to the provided value.

Usage:
  python scripts/setup_test_user.py <username> <email> <password>
"""

import asyncio
import sys
import os

import bcrypt
import asyncpg
from dotenv import load_dotenv

load_dotenv()


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


async def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/setup_test_user.py <username> <email> <password>")
        sys.exit(2)

    username, email, password = sys.argv[1], sys.argv[2], sys.argv[3]

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set")
        sys.exit(1)
    conn_str = db_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(conn_str)
    try:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE username=$1 OR email=$2", username, email
        )
        hashed = hash_password(password)
        if existing:
            await conn.execute(
                """
                UPDATE users
                SET hashed_password = $1,
                    email_verified  = TRUE,
                    is_active       = TRUE,
                    is_banned       = FALSE,
                    two_factor_enabled = FALSE,
                    two_factor_secret = NULL
                WHERE username=$2 OR email=$3
                """,
                hashed, username, email,
            )
            print(f"Updated existing test user (id={existing['id']}). Ready.")
        else:
            await conn.execute(
                """
                INSERT INTO users (
                    email, username, hashed_password, role,
                    is_active, is_banned, email_verified,
                    two_factor_enabled, created_at
                )
                VALUES ($1, $2, $3, 'USER', TRUE, FALSE, TRUE, FALSE, NOW())
                """,
                email, username, hashed,
            )
            print("Created new test user. Ready.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
