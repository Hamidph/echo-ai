"""
Notification service for experiment completion events.

Sends email notifications and dispatches webhooks when experiments complete.
"""

import json
import logging
from datetime import UTC, datetime

import httpx

from backend.app.services.email import send_email

logger = logging.getLogger(__name__)

EXPERIMENT_COMPLETE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .metric { background: #f5f5f5; padding: 12px; border-radius: 6px; margin: 8px 0; }
        .button { background: #4F46E5; color: white; padding: 12px 24px;
                  text-decoration: none; border-radius: 4px; display: inline-block; }
        .footer { margin-top: 30px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Your Experiment is Complete</h1>
        <p>Hi {{ user_name }},</p>
        <p>Your visibility experiment for <strong>{{ target_brand }}</strong> has finished running.</p>

        <h3>Key Results</h3>
        <div class="metric"><strong>Prompt:</strong> {{ prompt }}</div>
        <div class="metric"><strong>Visibility Rate:</strong> {{ visibility_rate }}%</div>
        <div class="metric"><strong>Share of Voice:</strong> {{ share_of_voice }}%</div>
        <div class="metric"><strong>Iterations Completed:</strong> {{ successful_iterations }} / {{ total_iterations }}</div>

        <p style="margin: 30px 0;">
            <a href="{{ experiment_url }}" class="button">View Full Report</a>
        </p>

        <div class="footer">
            <p>You received this email because experiment notifications are enabled for your account.</p>
            <p>&copy; 2024 Echo AI. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


async def send_experiment_complete_email(
    user_email: str,
    user_name: str,
    experiment_id: str,
    target_brand: str,
    prompt: str,
    visibility_rate: float,
    share_of_voice: float,
    successful_iterations: int,
    total_iterations: int,
    frontend_url: str,
) -> None:
    """
    Send an email notification when an experiment completes.

    Args:
        user_email: Recipient email address.
        user_name: User's display name.
        experiment_id: UUID of the completed experiment.
        target_brand: Brand that was analyzed.
        prompt: The prompt that was run.
        visibility_rate: Visibility rate percentage (0-100).
        share_of_voice: Share of voice percentage (0-100).
        successful_iterations: Number of successful iterations.
        total_iterations: Total iterations attempted.
        frontend_url: Base URL for building experiment link.
    """
    from jinja2 import Template

    experiment_url = f"{frontend_url}/experiments/detail?id={experiment_id}"

    template = Template(EXPERIMENT_COMPLETE_TEMPLATE)
    html_content = template.render(
        user_name=user_name or "there",
        target_brand=target_brand,
        prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
        visibility_rate=round(visibility_rate, 1),
        share_of_voice=round(share_of_voice, 1),
        successful_iterations=successful_iterations,
        total_iterations=total_iterations,
        experiment_url=experiment_url,
    )

    try:
        await send_email(
            to_email=user_email,
            subject=f"Experiment complete: {target_brand} visibility results ready",
            html_content=html_content,
        )
        logger.info(
            f"Experiment completion email sent to {user_email} for experiment {experiment_id}"
        )
    except Exception as e:
        logger.error(
            f"Failed to send experiment completion email to {user_email}: {e}", exc_info=True
        )


async def dispatch_webhook(
    webhook_url: str,
    experiment_id: str,
    target_brand: str,
    status: str,
    visibility_rate: float,
    share_of_voice: float,
    successful_iterations: int,
    total_iterations: int,
) -> None:
    """
    Dispatch a webhook notification when an experiment completes.

    Sends a POST request with experiment results as JSON payload.

    Args:
        webhook_url: URL to POST the notification to.
        experiment_id: UUID of the completed experiment.
        target_brand: Brand that was analyzed.
        status: Final experiment status (completed/failed).
        visibility_rate: Visibility rate percentage (0-100).
        share_of_voice: Share of voice percentage (0-100).
        successful_iterations: Number of successful iterations.
        total_iterations: Total iterations attempted.
    """
    payload = {
        "event": "experiment.completed",
        "experiment_id": experiment_id,
        "target_brand": target_brand,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "results": {
            "visibility_rate": round(visibility_rate, 2),
            "share_of_voice": round(share_of_voice, 2),
            "successful_iterations": successful_iterations,
            "total_iterations": total_iterations,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                content=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "EchoAI-Webhook/1.0",
                },
            )
            response.raise_for_status()
            logger.info(
                f"Webhook dispatched to {webhook_url} for experiment {experiment_id}, "
                f"status={response.status_code}"
            )
    except httpx.TimeoutException:
        logger.warning(f"Webhook timeout for {webhook_url} (experiment {experiment_id})")
    except httpx.HTTPStatusError as e:
        logger.warning(
            f"Webhook HTTP error {e.response.status_code} for {webhook_url} "
            f"(experiment {experiment_id})"
        )
    except Exception as e:
        logger.error(
            f"Webhook dispatch failed for {webhook_url} (experiment {experiment_id}): {e}",
            exc_info=True,
        )
