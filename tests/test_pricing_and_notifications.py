"""
Tests for the pricing module and notifications service.
"""

import pytest

from backend.app.core.pricing import estimate_batch_cost_usd, estimate_cost_usd


class TestPricing:
    """Tests for cost estimation functions."""

    def test_estimate_cost_known_model(self) -> None:
        """Test cost estimation for a known model."""
        cost = estimate_cost_usd("gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # gpt-4o: $0.005 input + $0.015 output per 1K
        # 1K input = $0.005, 500 output = $0.0075 → $0.0125
        assert cost == pytest.approx(0.0125, rel=1e-3)

    def test_estimate_cost_unknown_model_uses_default(self) -> None:
        """Test that unknown models use default pricing."""
        cost_known = estimate_cost_usd("gpt-4o", prompt_tokens=1000, completion_tokens=1000)
        cost_unknown = estimate_cost_usd(
            "unknown-model-xyz", prompt_tokens=1000, completion_tokens=1000
        )

        # Unknown model should still return a non-zero cost
        assert cost_unknown > 0

    def test_estimate_cost_zero_tokens(self) -> None:
        """Test that zero tokens returns zero cost."""
        cost = estimate_cost_usd("gpt-4o", prompt_tokens=0, completion_tokens=0)
        assert cost == 0.0

    def test_estimate_batch_cost(self) -> None:
        """Test batch cost estimation."""
        cost = estimate_batch_cost_usd(
            "claude-3-haiku-20240307",
            total_prompt_tokens=5000,
            total_completion_tokens=2000,
        )
        # claude-3-haiku: $0.00025 input + $0.00125 output per 1K
        # 5K input = 5 * 0.00025 = $0.00125
        # 2K output = 2 * 0.00125 = $0.0025
        # Total = $0.00375
        assert cost == pytest.approx(0.00375, rel=1e-3)

    def test_cost_for_perplexity_sonar(self) -> None:
        """Test cost estimation for Perplexity sonar model."""
        cost = estimate_cost_usd("sonar", prompt_tokens=2000, completion_tokens=1000)
        assert cost > 0

    def test_cost_for_anthropic_model(self) -> None:
        """Test cost estimation for Anthropic Claude model."""
        cost = estimate_cost_usd(
            "claude-3-5-sonnet-20241022",
            prompt_tokens=10000,
            completion_tokens=5000,
        )
        # $0.003 input + $0.015 output per 1K
        # 10K input = $0.03, 5K output = $0.075 → $0.105
        assert cost == pytest.approx(0.105, rel=1e-3)

    def test_result_is_rounded(self) -> None:
        """Test that cost result is rounded to 6 decimal places."""
        cost = estimate_cost_usd("gpt-4o", prompt_tokens=1, completion_tokens=1)
        # Should have at most 6 decimal places
        assert cost == round(cost, 6)


class TestNotificationsModule:
    """Tests for the notifications service module."""

    @pytest.mark.asyncio
    async def test_send_experiment_complete_email_dev_mode(self) -> None:
        """Test that email sending works in dev mode (logs instead of sending)."""
        from backend.app.services.notifications import send_experiment_complete_email

        # In dev mode (no SMTP configured), it should log but not raise
        await send_experiment_complete_email(
            user_email="test@example.com",
            user_name="Test User",
            experiment_id="exp-123",
            target_brand="TestBrand",
            prompt="What is the best CRM?",
            visibility_rate=75.0,
            share_of_voice=40.0,
            successful_iterations=8,
            total_iterations=10,
            frontend_url="http://localhost:3000",
        )
        # No assertion needed - just verifying it doesn't raise

    @pytest.mark.asyncio
    async def test_dispatch_webhook_invalid_url(self) -> None:
        """Test that webhook dispatch with unreachable URL fails gracefully."""
        from backend.app.services.notifications import dispatch_webhook

        # Should not raise even if webhook URL is unreachable
        await dispatch_webhook(
            webhook_url="http://localhost:9999/nonexistent",
            experiment_id="exp-123",
            target_brand="TestBrand",
            status="completed",
            visibility_rate=75.0,
            share_of_voice=40.0,
            successful_iterations=8,
            total_iterations=10,
        )
        # No exception should propagate
