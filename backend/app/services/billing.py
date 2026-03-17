"""
Stripe billing service for subscription management.

This module handles all Stripe-related operations including:
- Customer creation
- Subscription management
- Payment method handling
- Webhook processing
"""

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.models.user import PricingTier, User

settings = get_settings()

# Initialize Stripe
if hasattr(settings, "stripe_api_key") and settings.stripe_api_key:
    stripe.api_key = settings.stripe_api_key

# Pricing tier to Stripe price ID mapping
# Monthly prices (USD). Annual price IDs use the _annual suffix in settings.
PRICE_IDS = {
    PricingTier.FREE: None,  # Free tier has no Stripe price
    PricingTier.STARTER: getattr(settings, "stripe_price_id_starter", None),
    PricingTier.GROWTH: getattr(settings, "stripe_price_id_growth", None),
    PricingTier.PRO: getattr(settings, "stripe_price_id_pro", None),
    PricingTier.ENTERPRISE: None,  # Enterprise is custom / contact sales
}

PRICE_IDS_ANNUAL = {
    PricingTier.FREE: None,
    PricingTier.STARTER: getattr(settings, "stripe_price_id_starter_annual", None),
    PricingTier.GROWTH: getattr(settings, "stripe_price_id_growth_annual", None),
    PricingTier.PRO: getattr(settings, "stripe_price_id_pro_annual", None),
    PricingTier.ENTERPRISE: None,
}

# Prompt quota per month. Each prompt runs Monte Carlo iterations.
# Pricing (USD): Free $0, Starter $49/30, Growth $149/100, Pro $349/300, Enterprise custom
TIER_QUOTAS = {
    PricingTier.FREE: 5,  # permanent free tier (25 during 14-day trial)
    PricingTier.STARTER: 30,  # $49/mo
    PricingTier.GROWTH: 100,  # $149/mo
    PricingTier.PRO: 300,  # $349/mo
    PricingTier.ENTERPRISE: 500,  # custom — overridden per contract
}

TRIAL_PROMPT_QUOTA = 25
TRIAL_DAYS = 14


async def create_stripe_customer(user: User) -> str:
    """
    Create a Stripe customer for a user.

    Args:
        user: User instance to create customer for.

    Returns:
        str: Stripe customer ID.

    Raises:
        stripe.error.StripeError: If customer creation fails.
    """
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={
            "user_id": str(user.id),
            "environment": settings.environment,
        },
    )
    return customer.id


async def create_checkout_session(
    user: User,
    pricing_tier: PricingTier,
    success_url: str,
    cancel_url: str,
    annual: bool = False,
) -> stripe.checkout.Session:
    """
    Create a Stripe Checkout session for subscription.

    Args:
        user: User initiating the checkout.
        pricing_tier: Target pricing tier.
        success_url: URL to redirect on success.
        cancel_url: URL to redirect on cancellation.
        annual: If True, use annual pricing (20% discount).

    Returns:
        stripe.checkout.Session: Checkout session object.

    Raises:
        ValueError: If pricing tier is invalid.
        stripe.error.StripeError: If session creation fails.
    """
    if pricing_tier in (PricingTier.FREE, PricingTier.ENTERPRISE):
        raise ValueError(f"Cannot create checkout session for {pricing_tier} tier")

    price_map = PRICE_IDS_ANNUAL if annual else PRICE_IDS
    price_id = price_map.get(pricing_tier)
    if not price_id:
        raise ValueError(f"No price ID configured for tier: {pricing_tier}")

    # Ensure user has a Stripe customer ID
    if not user.stripe_customer_id:
        user.stripe_customer_id = await create_stripe_customer(user)

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": str(user.id),
            "pricing_tier": pricing_tier.value,
        },
    )

    return session


async def create_portal_session(customer_id: str, return_url: str) -> stripe.billing_portal.Session:
    """
    Create a Stripe billing portal session.

    Allows customers to manage their subscription, payment methods, and billing history.

    Args:
        customer_id: Stripe customer ID.
        return_url: URL to return to after portal session.

    Returns:
        stripe.billing_portal.Session: Portal session object.
    """
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session


async def cancel_subscription(subscription_id: str) -> stripe.Subscription:
    """
    Cancel a Stripe subscription.

    Args:
        subscription_id: Stripe subscription ID.

    Returns:
        stripe.Subscription: Cancelled subscription object.
    """
    subscription = stripe.Subscription.delete(subscription_id)
    return subscription


async def upgrade_user_tier(
    user: User,
    new_tier: PricingTier,
    db: AsyncSession,
) -> None:
    """
    Upgrade user to a new pricing tier.

    Updates quota and resets usage counter.

    Args:
        user: User to upgrade.
        new_tier: New pricing tier.
        db: Database session.
    """
    user.pricing_tier = new_tier.value
    user.monthly_prompt_quota = TIER_QUOTAS[new_tier]
    user.prompts_used_this_month = 0

    await db.commit()
    await db.refresh(user)


async def downgrade_user_tier(
    user: User,
    new_tier: PricingTier,
    db: AsyncSession,
) -> None:
    """
    Downgrade user to a lower pricing tier.

    Args:
        user: User to downgrade.
        new_tier: New pricing tier.
        db: Database session.
    """
    user.pricing_tier = new_tier.value
    user.monthly_prompt_quota = TIER_QUOTAS[new_tier]
    # Don't reset usage to prevent abuse

    await db.commit()
    await db.refresh(user)


async def check_usage_quota(user: User) -> bool:
    """
    Check if user has remaining quota.

    Args:
        user: User to check.

    Returns:
        bool: True if user has quota remaining, False otherwise.
    """
    return user.prompts_used_this_month < user.monthly_prompt_quota


async def increment_usage(user: User, prompts: int, db: AsyncSession) -> None:
    """
    Increment user's usage counter.

    Args:
        user: User to increment usage for.
        prompts: Number of prompts to add (each prompt = 1 experiment with 10 iterations).
        db: Database session.
    """
    user.prompts_used_this_month += prompts
    await db.commit()
