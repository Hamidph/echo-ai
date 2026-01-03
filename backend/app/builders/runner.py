"""
RunnerBuilder - The Probabilistic Execution Engine.

This module implements the core Monte Carlo simulation logic for running
prompts N times across LLM providers to measure response variance.

Innovation: This is the heart of the "Probabilistic Visibility Engine".
By using asyncio.gather with controlled concurrency, we can run 50-100
iterations in parallel while respecting API rate limits. The statistical
variance in responses enables brand visibility calculations that
single-shot tools cannot provide.
"""

import asyncio
import logging
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import UUID

from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.builders.providers import (
    BaseLLMProvider,
    ProviderAuthError,
    ProviderError,
    RateLimitError,
    get_provider,
)
from backend.app.core.config import Settings, get_settings
from backend.app.schemas.llm import (
    LLMProvider as LLMProviderEnum,
)
from backend.app.schemas.llm import (
    LLMRequest,
    LLMResponse,
    Message,
    MessageRole,
)
from backend.app.schemas.runner import (
    BatchConfig,
    BatchResult,
    IterationResult,
    IterationStatus,
    RunnerProgress,
)

logger = logging.getLogger(__name__)


class RunnerBuilder:
    """
    The Probabilistic Execution Engine.

    This builder handles the parallel execution of N iterations of a prompt
    against an LLM provider. It uses asyncio.gather for concurrent execution
    and implements rate limiting via semaphores.

    Innovation: The runner treats every query as a statistical experiment,
    enabling Monte Carlo-style analysis of LLM response variance. This is
    the core differentiator that enables "Generative Risk Analytics".

    Attributes:
        settings: Application settings for defaults and limits.
        _semaphore: Asyncio semaphore for concurrency control.
        _progress_callback: Optional callback for progress updates.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        progress_callback: Any | None = None,
    ) -> None:
        """
        Initialize the RunnerBuilder.

        Args:
            settings: Application settings. Uses get_settings() if not provided.
            progress_callback: Optional async callback for progress updates.
                              Signature: async def callback(progress: RunnerProgress) -> None
        """
        self.settings = settings or get_settings()
        self._progress_callback = progress_callback
        # Initialize with default to prevent race conditions in concurrent tasks
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(10)

    async def run_batch(
        self,
        prompt: str,
        provider: LLMProviderEnum,
        iterations: int | None = None,
        config: BatchConfig | None = None,
    ) -> BatchResult:
        """
        Run a prompt N times against an LLM provider.

        This is the main entry point for probabilistic execution. It spawns
        N concurrent requests using asyncio.gather while respecting rate limits.

        Innovation: By running the same prompt multiple times, we capture the
        inherent randomness in LLM responses, enabling statistical analysis
        of brand visibility variance.

        Args:
            prompt: The user prompt to run N times.
            provider: The LLM provider to use.
            iterations: Number of iterations (overrides config if provided).
            config: Batch configuration. Uses defaults if not provided.

        Returns:
            BatchResult: Complete results from all iterations with statistics.

        Raises:
            ValueError: If iterations exceeds max_iterations setting.
            ProviderAuthError: If provider authentication fails.
        """
        # Build configuration
        config = config or BatchConfig()
        if iterations is not None:
            config = BatchConfig(
                iterations=iterations,
                max_concurrency=config.max_concurrency,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                model=config.model,
                system_prompt=config.system_prompt,
            )

        # Validate iterations against settings
        if config.iterations > self.settings.max_iterations:
            raise ValueError(
                f"Iterations ({config.iterations}) exceeds maximum allowed "
                f"({self.settings.max_iterations})"
            )

        # Initialize the provider
        llm_provider = get_provider(
            provider=provider,
            model=config.model,
        )

        # Create batch result
        batch_result = BatchResult(
            provider=provider,
            model=llm_provider.default_model if config.model is None else config.model,
            prompt=prompt,
            system_prompt=config.system_prompt,
            config=config,
            started_at=datetime.utcnow(),
        )

        # Initialize semaphore for concurrency control
        # Innovation: Semaphore prevents overwhelming the API with too many
        # concurrent requests, reducing rate limit errors
        self._semaphore = asyncio.Semaphore(config.max_concurrency)

        start_time = perf_counter()

        try:
            async with llm_provider:
                # Build the LLM request
                messages: list[Message] = []
                if config.system_prompt:
                    messages.append(Message(role=MessageRole.SYSTEM, content=config.system_prompt))
                messages.append(Message(role=MessageRole.USER, content=prompt))

                llm_request = LLMRequest(
                    messages=messages,
                    model=config.model,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )

                # Create tasks for all iterations
                # Innovation: asyncio.gather enables parallel execution,
                # dramatically reducing total batch time compared to sequential
                tasks = [
                    self._run_single_iteration(
                        provider=llm_provider,
                        request=llm_request,
                        iteration_index=i,
                        batch_id=batch_result.batch_id,
                        total_iterations=config.iterations,
                    )
                    for i in range(config.iterations)
                ]

                # Execute all iterations concurrently
                # return_exceptions=True ensures one failure doesn't cancel others
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        # Handle unexpected exceptions
                        iteration_result = IterationResult(
                            iteration_index=i,
                            status=IterationStatus.FAILED,
                            error_message=str(result),
                        )
                    elif isinstance(result, IterationResult):
                        iteration_result = result
                    else:
                        # Shouldn't happen, but handle gracefully
                        iteration_result = IterationResult(
                            iteration_index=i,
                            status=IterationStatus.FAILED,
                            error_message=f"Unexpected result type: {type(result)}",
                        )
                    batch_result.iterations.append(iteration_result)

        finally:
            # Record completion time
            batch_result.completed_at = datetime.utcnow()
            batch_result.total_duration_ms = (perf_counter() - start_time) * 1000

        # Compute aggregated statistics
        batch_result.compute_statistics()

        logger.info(
            f"Batch {batch_result.batch_id} completed: "
            f"{batch_result.successful_iterations}/{batch_result.total_iterations} successful "
            f"in {batch_result.total_duration_ms:.2f}ms"
        )

        return batch_result

    async def _run_single_iteration(
        self,
        provider: BaseLLMProvider,
        request: LLMRequest,
        iteration_index: int,
        batch_id: UUID,
        total_iterations: int,
    ) -> IterationResult:
        """
        Run a single iteration with rate limiting and error handling.

        This method is called N times concurrently by asyncio.gather.
        It uses a semaphore to control concurrency and implements
        retry logic for transient failures.

        Args:
            provider: The LLM provider instance.
            request: The LLM request to execute.
            iteration_index: Zero-based index of this iteration.
            batch_id: Parent batch identifier.
            total_iterations: Total number of iterations in the batch.

        Returns:
            IterationResult: Result of this single iteration.
        """
        start_time = perf_counter()
        retry_count = 0

        async with self._semaphore:
            try:
                # The provider.generate method already has tenacity retry
                # for rate limits, but we add our own handling for tracking
                response = await self._execute_with_retry(
                    provider=provider,
                    request=request,
                )

                latency_ms = (perf_counter() - start_time) * 1000

                result = IterationResult(
                    iteration_index=iteration_index,
                    status=IterationStatus.SUCCESS,
                    response=response,
                    latency_ms=latency_ms,
                    retry_count=retry_count,
                )

            except RateLimitError as e:
                latency_ms = (perf_counter() - start_time) * 1000
                result = IterationResult(
                    iteration_index=iteration_index,
                    status=IterationStatus.RATE_LIMITED,
                    error_message=str(e),
                    latency_ms=latency_ms,
                )
                logger.warning(f"Iteration {iteration_index} rate limited: {e}")

            except ProviderAuthError as e:
                latency_ms = (perf_counter() - start_time) * 1000
                result = IterationResult(
                    iteration_index=iteration_index,
                    status=IterationStatus.AUTH_ERROR,
                    error_message=str(e),
                    latency_ms=latency_ms,
                )
                logger.error(f"Iteration {iteration_index} auth error: {e}")

            except ProviderError as e:
                latency_ms = (perf_counter() - start_time) * 1000
                # Check if it's a timeout
                status = (
                    IterationStatus.TIMEOUT
                    if "timeout" in str(e).lower()
                    else IterationStatus.FAILED
                )
                result = IterationResult(
                    iteration_index=iteration_index,
                    status=status,
                    error_message=str(e),
                    latency_ms=latency_ms,
                )
                logger.warning(f"Iteration {iteration_index} failed: {e}")

            except RetryError as e:
                # Tenacity exhausted all retries
                latency_ms = (perf_counter() - start_time) * 1000
                result = IterationResult(
                    iteration_index=iteration_index,
                    status=IterationStatus.RATE_LIMITED,
                    error_message=f"Exhausted retries: {e}",
                    latency_ms=latency_ms,
                )
                logger.warning(f"Iteration {iteration_index} exhausted retries: {e}")

            except Exception as e:
                latency_ms = (perf_counter() - start_time) * 1000
                result = IterationResult(
                    iteration_index=iteration_index,
                    status=IterationStatus.FAILED,
                    error_message=f"Unexpected error: {e}",
                    latency_ms=latency_ms,
                )
                logger.exception(f"Iteration {iteration_index} unexpected error")

        # Send progress update if callback is configured
        await self._send_progress(
            batch_id=batch_id,
            completed=iteration_index + 1,
            total=total_iterations,
            success=result.status == IterationStatus.SUCCESS,
        )

        return result

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _execute_with_retry(
        self,
        provider: BaseLLMProvider,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Execute a single LLM request with retry logic.

        Uses tenacity for exponential backoff on rate limit errors.
        This is separate from the provider's internal retry to allow
        for batch-level retry tracking.

        Args:
            provider: The LLM provider instance.
            request: The LLM request to execute.

        Returns:
            LLMResponse: The successful response.

        Raises:
            RateLimitError: If rate limit persists after retries.
            ProviderError: For non-retryable errors.
        """
        return await provider.generate(request)

    async def _send_progress(
        self,
        batch_id: UUID,
        completed: int,
        total: int,
        success: bool,
    ) -> None:
        """
        Send a progress update via the callback if configured.

        Args:
            batch_id: The batch identifier.
            completed: Number of completed iterations.
            total: Total iterations.
            success: Whether the last iteration was successful.
        """
        if self._progress_callback is None:
            return

        # Track cumulative success/failure (simplified - real impl would track state)
        progress = RunnerProgress(
            batch_id=batch_id,
            completed=completed,
            total=total,
            successful=completed if success else completed - 1,  # Simplified
            failed=0 if success else 1,  # Simplified
            progress_percent=(completed / total) * 100 if total > 0 else 0,
        )

        try:
            if asyncio.iscoroutinefunction(self._progress_callback):
                await self._progress_callback(progress)
            else:
                self._progress_callback(progress)
        except Exception as e:
            logger.warning(f"Progress callback failed: {e}")


async def run_batch(
    prompt: str,
    provider: LLMProviderEnum,
    iterations: int = 10,
    max_concurrency: int = 10,
    temperature: float = 0.7,
    system_prompt: str | None = None,
    model: str | None = None,
) -> BatchResult:
    """
    Convenience function to run a probabilistic batch.

    This is the simplest way to run a Monte Carlo simulation of a prompt.

    Innovation: This single function encapsulates the entire probabilistic
    engine, making it easy to run experiments from anywhere in the codebase.

    Args:
        prompt: The prompt to run N times.
        provider: The LLM provider to use.
        iterations: Number of iterations (default: 10).
        max_concurrency: Maximum concurrent requests (default: 10).
        temperature: Sampling temperature (default: 0.7 for variety).
        system_prompt: Optional system prompt.
        model: Optional model override.

    Returns:
        BatchResult: Complete results with statistics.

    Example:
        ```python
        result = await run_batch(
            prompt="What are the best CRM tools for startups?",
            provider=LLMProvider.PERPLEXITY,
            iterations=50,
        )
        print(f"Success rate: {result.success_rate:.1%}")
        print(f"Responses: {len(result.raw_responses)}")
        ```
    """
    config = BatchConfig(
        iterations=iterations,
        max_concurrency=max_concurrency,
        temperature=temperature,
        system_prompt=system_prompt,
        model=model,
    )

    runner = RunnerBuilder()
    return await runner.run_batch(
        prompt=prompt,
        provider=provider,
        config=config,
    )
