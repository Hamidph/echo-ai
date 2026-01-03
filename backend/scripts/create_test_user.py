import asyncio
import sys
import os

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from sqlalchemy import select
from backend.app.core.database import get_session_factory
from backend.app.models.user import User, PricingTier
from backend.app.core.security import get_password_hash

async def create_test_user():
    print("Connecting to database...")
    try:
        session_factory = get_session_factory()
    except Exception as e:
        print(f"Failed to create session factory: {e}")
        return

    async with session_factory() as session:
        email = "test@echoai.com"
        password = "password123"
        hashed_password = get_password_hash(password)
        
        print(f"Checking for user {email}...")
        try:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if user:
                print(f"User {email} exists. Updating quota to Unlimited (1M)...")
                user.monthly_prompt_quota = 1000000
                user.pricing_tier = PricingTier.ENTERPRISE
                user.hashed_password = hashed_password # Update password just in case
                user.is_active = True
                user.is_verified = True
                session.add(user)
            else:
                print(f"User {email} not found. Creating...")
                # Use string value for Enum if needed, but SQLAlchemy usually handles Enum objects if mapped correctly.
                # In User model: pricing_tier: Mapped[str] = mapped_column(...) default=PricingTier.FREE.value
                # The model definition uses `default=PricingTier.FREE.value`, which suggests it stores the string value.
                # However, the field type is String. I should assign the .value just to be safe if it expects a string.
                
                user = User(
                    email=email,
                    hashed_password=hashed_password,
                    full_name="Test Account",
                    is_active=True,
                    is_verified=True,
                    pricing_tier=PricingTier.ENTERPRISE.value,
                    monthly_prompt_quota=1000000,
                    role="admin"
                )
                session.add(user)
                
            await session.commit()
            print(f"Success! User: {email} / {password}")
        except Exception as e:
            print(f"Database error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(create_test_user())
