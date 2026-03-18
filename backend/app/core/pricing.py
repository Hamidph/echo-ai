"""
LLM Provider pricing constants for cost estimation.

Prices are in USD per 1,000 tokens (as of early 2026).
Update these values when providers change their pricing.
"""

# Cost per 1,000 tokens in USD: {model: (input_cost, output_cost)}
MODEL_PRICING: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (0.005, 0.015),
    "gpt-4-turbo": (0.010, 0.030),
    "gpt-4": (0.030, 0.060),
    "gpt-3.5-turbo": (0.0005, 0.0015),
    # Anthropic
    "claude-3-opus-20240229": (0.015, 0.075),
    "claude-3-5-sonnet-20241022": (0.003, 0.015),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
    "claude-3-sonnet-20240229": (0.003, 0.015),
    "claude-sonnet-4-6": (0.003, 0.015),
    # Perplexity (sonar models)
    "sonar": (0.001, 0.001),
    "sonar-pro": (0.003, 0.015),
    "sonar-reasoning": (0.001, 0.005),
}

# Default cost when model is unknown (conservative estimate)
DEFAULT_INPUT_COST_PER_1K = 0.003
DEFAULT_OUTPUT_COST_PER_1K = 0.015


def estimate_cost_usd(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """
    Estimate the cost of an LLM API call in USD.

    Args:
        model: The model name used (e.g., "gpt-4o", "claude-3-haiku-20240307").
        prompt_tokens: Number of input/prompt tokens consumed.
        completion_tokens: Number of output/completion tokens generated.

    Returns:
        float: Estimated cost in USD.
    """
    # Normalize model name for lookup (strip version suffixes if needed)
    input_cost_per_1k, output_cost_per_1k = MODEL_PRICING.get(
        model,
        (DEFAULT_INPUT_COST_PER_1K, DEFAULT_OUTPUT_COST_PER_1K),
    )

    input_cost = (prompt_tokens / 1000) * input_cost_per_1k
    output_cost = (completion_tokens / 1000) * output_cost_per_1k

    return round(input_cost + output_cost, 6)


def estimate_batch_cost_usd(
    model: str,
    total_prompt_tokens: int,
    total_completion_tokens: int,
) -> float:
    """
    Estimate the total cost of a batch run in USD.

    Args:
        model: The model name used.
        total_prompt_tokens: Total prompt tokens across all iterations.
        total_completion_tokens: Total completion tokens across all iterations.

    Returns:
        float: Estimated total cost in USD.
    """
    return estimate_cost_usd(model, total_prompt_tokens, total_completion_tokens)
