"""
Seed test data for demo and development purposes.

This script creates:
1. Test user account (test@echoai.com)
2. Sample experiments with realistic data
3. Complete batch runs and iterations

Run this after migrations to populate the database with demo data.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from sqlalchemy import select
from backend.app.core.database import get_session_factory
from backend.app.models.user import User, PricingTier, UserRole
from backend.app.models.experiment import (
    Experiment,
    BatchRun,
    Iteration,
    ExperimentStatus,
    ExperimentFrequency,
    BatchRunStatus,
)
from backend.app.core.security import get_password_hash


# Sample experiment data for realistic demos
SAMPLE_EXPERIMENTS = [
    {
        "prompt": "What are the best CRM tools for startups in 2026?",
        "target_brand": "Salesforce",
        "competitor_brands": ["HubSpot", "Pipedrive", "Zoho CRM"],
        "provider": "openai",
        "model": "gpt-4o",
        "iterations": 10,
        "visibility_rate": 0.85,
        "avg_position": 1.2,
        "status": ExperimentStatus.COMPLETED,
        "days_ago": 1,
    },
    {
        "prompt": "Top project management software for remote teams",
        "target_brand": "Asana",
        "competitor_brands": ["Monday.com", "Trello", "ClickUp"],
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "iterations": 10,
        "visibility_rate": 0.70,
        "avg_position": 2.5,
        "status": ExperimentStatus.COMPLETED,
        "days_ago": 2,
    },
    {
        "prompt": "Best email marketing platforms for small business",
        "target_brand": "Mailchimp",
        "competitor_brands": ["ConvertKit", "ActiveCampaign", "Sendinblue"],
        "provider": "openai",
        "model": "gpt-4o",
        "iterations": 10,
        "visibility_rate": 0.90,
        "avg_position": 1.0,
        "status": ExperimentStatus.COMPLETED,
        "days_ago": 3,
    },
    {
        "prompt": "Affordable alternatives to Adobe Creative Cloud",
        "target_brand": "Canva",
        "competitor_brands": ["Figma", "Affinity Designer", "Sketch"],
        "provider": "openai",
        "model": "gpt-4o",
        "iterations": 10,
        "visibility_rate": 0.95,
        "avg_position": 1.0,
        "status": ExperimentStatus.COMPLETED,
        "days_ago": 5,
    },
    {
        "prompt": "Best accounting software for freelancers",
        "target_brand": "QuickBooks",
        "competitor_brands": ["FreshBooks", "Wave", "Xero"],
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "iterations": 10,
        "visibility_rate": 0.60,
        "avg_position": 3.0,
        "status": ExperimentStatus.COMPLETED,
        "days_ago": 7,
    },
]


async def create_or_update_test_user(session):
    """Create or update the test user account."""
    email = "test@echoai.com"
    password = "password123"
    hashed_password = get_password_hash(password)
    
    print(f"Checking for user {email}...")
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        print(f"✓ User {email} exists (ID: {user.id})")
        # Update to ensure correct configuration
        user.monthly_prompt_quota = 1000000
        user.pricing_tier = PricingTier.ENTERPRISE.value
        user.hashed_password = hashed_password
        user.is_active = True
        user.is_verified = True
        user.role = UserRole.ADMIN.value
        session.add(user)
    else:
        print(f"Creating user {email}...")
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name="Test Account",
            is_active=True,
            is_verified=True,
            pricing_tier=PricingTier.ENTERPRISE.value,
            monthly_prompt_quota=1000000,
            prompts_used_this_month=0,
            role=UserRole.ADMIN.value,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        print(f"✓ Created user {email} (ID: {user.id})")
    
    await session.commit()
    await session.refresh(user)
    return user


async def create_sample_experiment(session, user_id, exp_data):
    """Create a sample experiment with complete data."""
    created_at = datetime.now(timezone.utc) - timedelta(days=exp_data["days_ago"])
    
    # Create experiment (set as recurring with daily frequency)
    experiment = Experiment(
        user_id=user_id,
        prompt=exp_data["prompt"],
        target_brand=exp_data["target_brand"],
        competitor_brands=exp_data["competitor_brands"],
        config={
            "llm_provider": exp_data["provider"],
            "model": exp_data["model"],
            "iterations": exp_data["iterations"],
            "temperature": 0.7,
        },
        status=exp_data["status"].value,
        is_recurring=True,
        frequency=ExperimentFrequency.DAILY.value,
        next_run_at=datetime.now(timezone.utc) + timedelta(days=1),
        last_run_at=created_at + timedelta(minutes=5),
        created_at=created_at,
        updated_at=created_at + timedelta(minutes=5),
    )
    session.add(experiment)
    await session.flush()
    await session.refresh(experiment)
    
    # Create batch run
    batch_run = BatchRun(
        experiment_id=experiment.id,
        provider=exp_data["provider"],
        model=exp_data["model"],
        status=BatchRunStatus.COMPLETED.value,
        started_at=created_at + timedelta(seconds=10),
        completed_at=created_at + timedelta(minutes=5),
        duration_ms=290000,  # ~5 minutes
        total_iterations=exp_data["iterations"],
        successful_iterations=exp_data["iterations"],
        failed_iterations=0,
        total_tokens=exp_data["iterations"] * 500,  # Realistic token count
        metrics={
            "target_visibility": {
                "visibility_rate": exp_data["visibility_rate"],
                "confidence_interval_95": [exp_data["visibility_rate"] - 0.05, exp_data["visibility_rate"] + 0.05],
            },
            "share_of_voice": [
                {"brand": exp_data["target_brand"], "share": exp_data["visibility_rate"]},
            ] + [
                {"brand": comp, "share": (1 - exp_data["visibility_rate"]) / len(exp_data["competitor_brands"])}
                for comp in exp_data["competitor_brands"]
            ],
            "avg_position": exp_data["avg_position"],
            "consistency_score": exp_data["visibility_rate"],
        },
    )
    session.add(batch_run)
    await session.flush()
    await session.refresh(batch_run)
    
    # Create iterations
    iterations = []
    for i in range(exp_data["iterations"]):
        # Determine if brand is mentioned based on visibility rate
        brand_mentioned = i < int(exp_data["iterations"] * exp_data["visibility_rate"])
        
        iteration = Iteration(
            batch_run_id=batch_run.id,
            iteration_index=i,
            raw_response=f"Sample response for iteration {i+1}. " + 
                        (f"{exp_data['target_brand']} is a great option for this use case." if brand_mentioned else "Here are some alternatives to consider."),
            latency_ms=2000 + (i * 100),  # Realistic latency
            is_success=True,
            status="completed",
            extracted_brands=[exp_data["target_brand"]] if brand_mentioned else [],
            prompt_tokens=250,
            completion_tokens=250,
            total_tokens=500,
        )
        iterations.append(iteration)
    
    session.add_all(iterations)
    await session.flush()
    
    print(f"  ✓ Created experiment: {exp_data['prompt'][:50]}... ({exp_data['status'].value})")
    return experiment


async def seed_test_data():
    """Main function to seed all test data."""
    print("=" * 80)
    print("SEEDING TEST DATA FOR ECHO AI")
    print("=" * 80)
    print()
    
    try:
        session_factory = get_session_factory()
    except Exception as e:
        print(f"❌ Failed to create session factory: {e}")
        return False
    
    async with session_factory() as session:
        try:
            # Step 1: Create/update test user
            print("Step 1: Creating test user...")
            user = await create_or_update_test_user(session)
            print()
            
            # Step 2: Check if experiments already exist
            print("Step 2: Checking existing experiments...")
            result = await session.execute(
                select(Experiment).where(Experiment.user_id == user.id)
            )
            existing_experiments = result.scalars().all()
            
            # Update existing experiments to be recurring
            if len(existing_experiments) > 0:
                print(f"✓ Found {len(existing_experiments)} existing experiments. Updating to recurring...")
                for exp in existing_experiments:
                    exp.is_recurring = True
                    exp.frequency = ExperimentFrequency.DAILY.value
                    exp.next_run_at = datetime.now(timezone.utc) + timedelta(days=1)
                    if not exp.last_run_at:
                        exp.last_run_at = exp.updated_at
                    session.add(exp)
                await session.commit()
                print(f"✓ Updated {len(existing_experiments)} experiments to daily recurring")
                print()
                print("=" * 80)
                print("Test data updated to recurring!")
                print("=" * 80)
                return True
            
            print(f"Found {len(existing_experiments)} existing experiments. Creating samples...")
            print()
            
            # Step 3: Create sample experiments
            print("Step 3: Creating sample experiments... (SKIPPED FOR PROD)")
            # PRODUCTION: Do not create dummy experiments
            # for exp_data in SAMPLE_EXPERIMENTS:
            #     await create_sample_experiment(session, user.id, exp_data)
            
            await session.commit()
            print()
            
            # Step 4: Verify
            print("Step 4: Verifying data...")
            result = await session.execute(
                select(Experiment).where(Experiment.user_id == user.id)
            )
            total_experiments = len(result.scalars().all())
            
            print(f"✓ Total experiments for {user.email}: {total_experiments}")
            print()
            
            print("=" * 80)
            print("SUCCESS! Test data seeded successfully")
            print("=" * 80)
            print()
            print("Test Account Credentials:")
            print(f"  Email: test@echoai.com")
            print(f"  Password: password123")
            print(f"  Experiments: {total_experiments}")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error seeding data: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = asyncio.run(seed_test_data())
    sys.exit(0 if success else 1)
