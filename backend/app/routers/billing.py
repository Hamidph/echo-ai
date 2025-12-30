"""
Billing and subscription management endpoints.

This module provides routes for Stripe integration including:
- Checkout session creation
- Subscription management
- Webhook handling
"""

import hmac
import hashlib
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_active_user
from backend.app.models.user import PricingTier, User
from backend.app.services.billing import (
    create_checkout_session,
    create_portal_session,
    downgrade_user_tier,
    upgrade_user_tier,
)

settings = get_settings()
router = APIRouter(prefix="/billing", tags=["Billing"])


# Request/Response schemas
class CheckoutSessionCreate(BaseModel):
    """Schema for creating a checkout session."""

    pricing_tier: PricingTier
    success_url: HttpUrl
    cancel_url: HttpUrl


class CheckoutSessionResponse(BaseModel):
    """Schema for checkout session response."""

    session_id: str
    url: str


class PortalSessionResponse(BaseModel):
    """Schema for portal session response."""

    url: str


class UsageResponse(BaseModel):
    """Schema for usage information."""

    iterations_used: int
    monthly_quota: int
    remaining: int
    percentage_used: float
    pricing_tier: str


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    checkout_data: CheckoutSessionCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CheckoutSessionResponse:
    """
    Create a Stripe Checkout session for subscription upgrade.

    The user will be redirected to Stripe's hosted checkout page.
    """
    try:
        session = await create_checkout_session(
            user=current_user,
            pricing_tier=checkout_data.pricing_tier,
            success_url=str(checkout_data.success_url),
            cancel_url=str(checkout_data.cancel_url),
        )

        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}",
        )


@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal(
    current_user: Annotated[User, Depends(get_current_active_user)],
    return_url: HttpUrl,
) -> PortalSessionResponse:
    """
    Create a Stripe billing portal session.

    Allows users to manage subscriptions, payment methods, and view invoices.
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found. Please subscribe first.",
        )

    try:
        session = await create_portal_session(
            customer_id=current_user.stripe_customer_id,
            return_url=str(return_url),
        )

        return PortalSessionResponse(url=session.url)
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stripe error: {str(e)}",
        )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UsageResponse:
    """
    Get current usage statistics for the user.
    """
    remaining = current_user.monthly_iteration_quota - current_user.iterations_used_this_month
    percentage_used = (
        (current_user.iterations_used_this_month / current_user.monthly_iteration_quota) * 100
        if current_user.monthly_iteration_quota > 0
        else 0
    )

    return UsageResponse(
        iterations_used=current_user.iterations_used_this_month,
        monthly_quota=current_user.monthly_iteration_quota,
        remaining=remaining,
        percentage_used=round(percentage_used, 2),
        pricing_tier=current_user.pricing_tier,
    )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    stripe_signature: Annotated[str | None, Header(alias="stripe-signature")] = None,
) -> dict[str, str]:
    """
    Handle Stripe webhook events.

    Processes subscription lifecycle events and updates user data accordingly.

    Events handled:
    - checkout.session.completed: Upgrade user tier
    - customer.subscription.updated: Update subscription status
    - customer.subscription.deleted: Downgrade to free tier
    - invoice.payment_succeeded: Reset monthly quota
    - invoice.payment_failed: Handle failed payment
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header",
        )

    # Get webhook secret from settings
    webhook_secret = getattr(settings, 'stripe_webhook_secret', None)
    if not webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    # Get raw request body
    payload = await request.body()

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        # Payment successful, upgrade user
        user_id = data.get("metadata", {}).get("user_id")
        pricing_tier = data.get("metadata", {}).get("pricing_tier")

        if user_id and pricing_tier:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if user:
                user.stripe_subscription_id = data.get("subscription")
                await upgrade_user_tier(user, PricingTier(pricing_tier), db)

    elif event_type == "customer.subscription.deleted":
        # Subscription cancelled, downgrade to free
        subscription_id = data["id"]

        result = await db.execute(
            select(User).where(User.stripe_subscription_id == subscription_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.stripe_subscription_id = None
            await downgrade_user_tier(user, PricingTier.FREE, db)

    elif event_type == "invoice.payment_succeeded":
        # Monthly payment succeeded, reset quota
        subscription_id = data.get("subscription")

        if subscription_id:
            result = await db.execute(
                select(User).where(User.stripe_subscription_id == subscription_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.iterations_used_this_month = 0
                await db.commit()

    elif event_type == "invoice.payment_failed":
        # Payment failed, notify user (implement notification system)
        pass

    return {"status": "success"}
