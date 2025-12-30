#!/usr/bin/env python3
"""
Database initialization script.

This script creates the database schema and optionally seeds initial data.
Run this before starting the application for the first time.

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --seed  # Also create seed data
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.config import get_settings
from backend.app.core.database import Base, get_engine
from backend.app.core.security import get_password_hash
from backend.app.models.experiment import BatchRun, Experiment, Iteration  # noqa: F401
from backend.app.models.user import APIKey, User, UserRole, PricingTier  # noqa: F401


async def init_database(seed: bool = False) -> None:
    """
    Initialize the database schema.

    Args:
        seed: Whether to create seed data for testing.
    """
    settings = get_settings()
    engine = get_engine()

    print(f"Initializing database: {settings.postgres_db}")
    print(f"Host: {settings.postgres_host}")

    # Create all tables
    async with engine.begin() as conn:
        print("Creating database schema...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ Schema created successfully")

    if seed:
        print("\nSeeding database with initial data...")
        from sqlalchemy.ext.asyncio import AsyncSession

        async with AsyncSession(engine) as session:
            # Create admin user
            admin_user = User(
                email="admin@ai-visibility.com",
                hashed_password=get_password_hash("admin123"),  # Change in production!
                full_name="Admin User",
                role=UserRole.ADMIN.value,
                pricing_tier=PricingTier.ENTERPRISE.value,
                monthly_iteration_quota=1000000,
                is_active=True,
                is_verified=True,
            )
            session.add(admin_user)

            # Create test user
            test_user = User(
                email="test@example.com",
                hashed_password=get_password_hash("test123"),
                full_name="Test User",
                role=UserRole.USER.value,
                pricing_tier=PricingTier.FREE.value,
                monthly_iteration_quota=100,
                is_active=True,
                is_verified=True,
            )
            session.add(test_user)

            await session.commit()
            print("✓ Seed data created successfully")
            print("\nTest credentials:")
            print("  Admin: admin@ai-visibility.com / admin123")
            print("  User:  test@example.com / test123")
            print("\n⚠️  IMPORTANT: Change these passwords in production!")

    await engine.dispose()
    print("\n✓ Database initialization complete!")


async def check_database_connection() -> bool:
    """
    Check if the database connection is working.

    Returns:
        bool: True if connection successful, False otherwise.
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument("--seed", action="store_true", help="Create seed data for testing")
    parser.add_argument(
        "--check", action="store_true", help="Only check database connection"
    )
    args = parser.parse_args()

    if args.check:
        print("Checking database connection...")
        if await check_database_connection():
            print("✓ Database connection successful")
            sys.exit(0)
        else:
            sys.exit(1)

    # Check connection first
    print("Checking database connection...")
    if not await check_database_connection():
        print("\n✗ Cannot connect to database. Please check your configuration.")
        print("  - Ensure PostgreSQL is running")
        print("  - Check POSTGRES_* environment variables in .env")
        sys.exit(1)

    print("✓ Database connection successful\n")

    # Initialize database
    await init_database(seed=args.seed)


if __name__ == "__main__":
    asyncio.run(main())
