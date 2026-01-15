"""
LLM Provider adapters implementing a unified interface.

This module provides the abstract base class and concrete implementations
for interacting with various LLM providers (OpenAI, Anthropic, Perplexity).

Innovation: The unified provider interface enables the probabilistic engine
to run identical experiments across different LLMs, measuring variance in
brand visibility recommendations between providers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from time import perf_counter
from typing import Any

import logging
import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.core.config import get_settings
from backend.app.schemas.llm import (
    LLMProvider as LLMProviderEnum,
)
from backend.app.schemas.llm import (
    LLMRequest,
    LLMResponse,
    Message,
    MessageRole,
    PerplexityResponse,
    PerplexitySearchResult,
    UsageInfo,
)


logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when an API rate limit is hit."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ProviderAuthError(Exception):
    """Raised when API authentication fails."""

    pass


class ProviderError(Exception):
    """Generic provider error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ProviderServerError(ProviderError):
    """Raised when the provider returns a 5xx error (retryable)."""
    pass


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    All provider implementations must inherit from this class and implement
    the async generate method. This ensures consistent interface across
    providers for the probabilistic engine.

    Innovation: The abstract design allows new providers to be added without
    modifying the core probabilistic engine logic.
    """

    def __init__(self, api_key: str, base_url: str, timeout: float = 30.0) -> None:
        """
        Initialize the provider with authentication and configuration.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for the provider's API.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    @abstractmethod
    def provider_name(self) -> LLMProviderEnum:
        """Return the provider enum value."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        ...

    async def get_client(self) -> httpx.AsyncClient:
        """
        Get or create the async HTTP client.

        Returns:
            httpx.AsyncClient: The HTTP client instance.
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self._client

    @abstractmethod
    def _get_headers(self) -> dict[str, str]:
        """
        Get provider-specific HTTP headers.

        Returns:
            dict: Headers including authentication.
        """
        ...

    @abstractmethod
    async def _make_request(
        self,
        request: LLMRequest,
    ) -> dict[str, Any]:
        """
        Make the actual API request to the provider.

        Args:
            request: The unified LLM request.

        Returns:
            dict: Raw response from the provider.

        Raises:
            RateLimitError: If rate limit is exceeded.
            ProviderAuthError: If authentication fails.
            ProviderError: For other API errors.
        """
        ...

    @abstractmethod
    def _parse_response(
        self,
        raw_response: dict[str, Any],
        latency_ms: float,
    ) -> LLMResponse:
        """
        Parse the provider's raw response into unified schema.

        Args:
            raw_response: Raw JSON response from the provider.
            latency_ms: Request latency in milliseconds.

        Returns:
            LLMResponse: Parsed response in unified format.
        """
        ...

    @retry(
        retry=retry_if_exception_type((RateLimitError, ProviderServerError)),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a completion from the LLM.

        This method handles retries for rate limits using tenacity.
        The @retry decorator implements exponential backoff.

        Args:
            request: The unified LLM request.

        Returns:
            LLMResponse: The generated response.

        Raises:
            RateLimitError: If rate limit exceeded after retries.
            ProviderAuthError: If authentication fails.
            ProviderError: For other API errors.
        """
        start_time = perf_counter()
        raw_response = await self._make_request(request)
        latency_ms = (perf_counter() - start_time) * 1000

        return self._parse_response(raw_response, latency_ms)

    async def generate_simple(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
        """
        Convenience method for simple single-turn generation.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt.

        Returns:
            LLMResponse: The generated response.
        """
        messages: list[Message] = []
        if system_prompt:
            messages.append(Message(role=MessageRole.SYSTEM, content=system_prompt))
        messages.append(Message(role=MessageRole.USER, content=prompt))

        request = LLMRequest(messages=messages)
        return await self.generate(request)

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "BaseLLMProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.close()


class PerplexityProvider(BaseLLMProvider):
    """
    Perplexity API provider implementation.

    Innovation: Perplexity's Sonar models provide web-grounded responses,
    enabling real-time brand visibility analysis with source citations.
    The search_results field allows tracking which sources mention brands.
    """

    # Perplexity model options
    MODEL_SONAR = "sonar"
    MODEL_SONAR_PRO = "sonar-pro"
    MODEL_SONAR_DEEP_RESEARCH = "sonar-deep-research"
    MODEL_SONAR_REASONING_PRO = "sonar-reasoning-pro"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL_SONAR,
        timeout: float = 60.0,
    ) -> None:
        """
        Initialize the Perplexity provider.

        Args:
            api_key: Perplexity API key. If None, loaded from settings.
            model: Default model to use.
            timeout: Request timeout in seconds.
        """
        settings = get_settings()
        resolved_api_key = api_key or settings.perplexity_api_key

        if not resolved_api_key:
            raise ProviderAuthError("Perplexity API key not configured")

        super().__init__(
            api_key=resolved_api_key,
            base_url="https://api.perplexity.ai",
            timeout=timeout,
        )
        self._default_model = model

    @property
    def provider_name(self) -> LLMProviderEnum:
        """Return the provider enum value."""
        return LLMProviderEnum.PERPLEXITY

    @property
    def default_model(self) -> str:
        """Return the default model for Perplexity."""
        return self._default_model

    def _get_headers(self) -> dict[str, str]:
        """Get Perplexity-specific headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    MAX_RETRIES = 3

    def _get_headers(self) -> dict[str, str]:
        """Get Perplexity-specific headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _make_request(self, request: LLMRequest) -> dict[str, Any]:
        """
        Make a chat completion request to Perplexity.

        Args:
            request: The unified LLM request.

        Returns:
            dict: Raw response from Perplexity.

        Raises:
            RateLimitError: If rate limit is exceeded (429).
            ProviderAuthError: If authentication fails (401/403).
            ProviderError: For other API errors.
        """
        client = await self.get_client()

        # Build Perplexity-specific payload
        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
            "temperature": request.temperature,
            "top_p": request.top_p,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            response = await client.post("/chat/completions", json=payload)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Perplexity rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                )

            if response.status_code in (401, 403):
                raise ProviderAuthError(f"Perplexity authentication failed: {response.text}")

            if response.status_code >= 500:
                raise ProviderServerError(
                    f"Perplexity server error: {response.text}",
                    status_code=response.status_code,
                )

            if response.status_code != 200:
                raise ProviderError(
                    f"Perplexity API error: {response.text}",
                    status_code=response.status_code,
                )

            result: dict[str, Any] = response.json()
            return result

        except httpx.TimeoutException as e:
            raise ProviderError(f"Perplexity request timeout: {e}") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Perplexity request failed: {e}") from e

    def _parse_response(
        self,
        raw_response: dict[str, Any],
        latency_ms: float,
    ) -> PerplexityResponse:
        """
        Parse Perplexity's response into unified schema.

        Args:
            raw_response: Raw JSON from Perplexity.
            latency_ms: Request latency in milliseconds.

        Returns:
            PerplexityResponse: Parsed response with search results.
        """
        # Extract the main completion
        choices = raw_response.get("choices", [])
        if not choices:
            raise ProviderError("No choices in Perplexity response")

        choice = choices[0]
        message = choice.get("message", {})

        # Parse usage info
        usage_data = raw_response.get("usage")
        usage = None
        if usage_data:
            usage = UsageInfo(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        # Parse search results (Perplexity-specific)
        search_results = None
        raw_search = raw_response.get("search_results")
        if raw_search:
            search_results = [
                PerplexitySearchResult(
                    title=sr.get("title", ""),
                    url=sr.get("url", ""),
                    date=sr.get("date"),
                )
                for sr in raw_search
            ]

        return PerplexityResponse(
            id=raw_response.get("id", ""),
            provider=self.provider_name,
            model=raw_response.get("model", self.default_model),
            content=message.get("content", ""),
            finish_reason=choice.get("finish_reason"),
            usage=usage,
            created_at=datetime.utcnow(),
            latency_ms=latency_ms,
            raw_response=raw_response,
            search_results=search_results,
        )


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider implementation using the new Responses API.
    
    Innovation: Uses the /v1/responses endpoint for stateful, advanced model interactions,
    mirroring the capabilities of the ChatGPT web interface.
    """

    MODEL_GPT5_2 = "gpt-5.2"
    MODEL_GPT4O = "gpt-4o"
    
    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL_GPT5_2,
        timeout: float = 60.0,
    ) -> None:
        """Initialize the OpenAI provider."""
        settings = get_settings()
        resolved_api_key = api_key or settings.openai_api_key

        if not resolved_api_key:
            raise ProviderAuthError("OpenAI API key not configured")

        super().__init__(
            api_key=resolved_api_key,
            base_url="https://api.openai.com/v1",
            timeout=timeout,
        )
        self._default_model = model

    @property
    def provider_name(self) -> LLMProviderEnum:
        """Return the provider enum value."""
        return LLMProviderEnum.OPENAI

    @property
    def default_model(self) -> str:
        """Return the default model for OpenAI."""
        return self._default_model

    def _get_headers(self) -> dict[str, str]:
        """Get OpenAI-specific headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _make_request(self, request: LLMRequest) -> dict[str, Any]:
        """
        Make a request to the OpenAI Responses API.
        POST /v1/responses
        """
        client = await self.get_client()

        # Transform messages for the Responses API
        # The 'input' field takes an array of message objects or strings
        input_items = []
        for m in request.messages:
            if m.role == MessageRole.SYSTEM:
                # Responses API handles instructions separately or as developer messages
                # For simplicity/compatibility, we'll map system to developer role if supported,
                # or just prepend as a message. Docs say 'instructions' field is for system/developer message.
                pass 
            else:
                input_items.append({
                    "role": m.role.value,
                    "content": m.content,
                    "type": "message" # Explicitly typed as message
                })

        # Extract system prompt if present
        instructions = None
        for m in request.messages:
            if m.role == MessageRole.SYSTEM:
                instructions = m.content
                break

        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "input": input_items,
            "stream": False, 
        }

        if instructions:
            payload["instructions"] = instructions
        
        # Temperature/Top_P handling
        # Note: gpt-4.5-preview and reasoning models might have restrictions, 
        # but the logic for excluding params is handled in generic ways or by the API ignoring them.
        # We'll include them if set, relying on the API or previous logic to filter if needed.
        # However, for Responses API, 'temperature' is a top-level param.
        if request.temperature is not None:
             payload["temperature"] = request.temperature
        
        if request.top_p is not None:
            payload["top_p"] = request.top_p

        if request.max_tokens:
            payload["max_output_tokens"] = request.max_tokens # Responses API uses max_output_tokens

        try:
            response = await client.post("/responses", json=payload)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "OpenAI rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                )

            if response.status_code in (401, 403):
                raise ProviderAuthError(f"OpenAI authentication failed: {response.text}")

            if response.status_code >= 500:
                raise ProviderServerError(
                    f"OpenAI server error: {response.text}",
                    status_code=response.status_code,
                )

            if response.status_code != 200:
                raise ProviderError(
                    f"OpenAI API error: {response.text}",
                    status_code=response.status_code,
                )

            result: dict[str, Any] = response.json()
            return result

        except httpx.TimeoutException as e:
            raise ProviderError(f"OpenAI request timeout: {e}") from e
        except httpx.RequestError as e:
            raise ProviderError(f"OpenAI request failed: {e}") from e

    def _parse_response(
        self,
        raw_response: dict[str, Any],
        latency_ms: float,
    ) -> LLMResponse:
        """Parse OpenAI Responses API response into unified schema."""
        # Responses API returns 'output' array containing messages
        output_items = raw_response.get("output", [])
        if not output_items:
            raise ProviderError("No output items in OpenAI response")

        # Find the assistant message in the output
        content = ""
        finish_reason = None
        
        for item in output_items:
            if item.get("type") == "message" and item.get("role") == "assistant":
                # Message content is a list of blocks
                message_content = item.get("content", [])
                for block in message_content:
                    if block.get("type") == "output_text":
                        content += block.get("text", "")
                
                finish_reason = item.get("status") # 'completed', etc.
                if item.get("id"):
                    # Use the message ID if available, or fall back to response ID
                    pass

        usage_data = raw_response.get("usage")
        usage = None
        if usage_data:
            usage = UsageInfo(
                prompt_tokens=usage_data.get("input_tokens", 0),
                completion_tokens=usage_data.get("output_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        return LLMResponse(
            id=raw_response.get("id", ""),
            provider=self.provider_name,
            model=raw_response.get("model", self.default_model),
            content=content,
            finish_reason=finish_reason,
            usage=usage,
            created_at=datetime.utcnow(),
            latency_ms=latency_ms,
            raw_response=raw_response,
        )


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude API provider implementation.

    Placeholder for Phase 2 completion - implements the interface
    but will be fully implemented when Anthropic integration is needed.
    """

    MODEL_CLAUDE_45_SONNET = "claude-sonnet-4-5-20250929"
    MODEL_CLAUDE_35_SONNET = "claude-3-5-sonnet-20240620"
    
    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL_CLAUDE_45_SONNET,
        timeout: float = 60.0,
    ) -> None:
        """Initialize the Anthropic provider."""
        settings = get_settings()
        resolved_api_key = api_key or settings.anthropic_api_key

        if not resolved_api_key:
            raise ProviderAuthError("Anthropic API key not configured")

        super().__init__(
            api_key=resolved_api_key,
            base_url="https://api.anthropic.com/v1",
            timeout=timeout,
        )
        self._default_model = model

    @property
    def provider_name(self) -> LLMProviderEnum:
        """Return the provider enum value."""
        return LLMProviderEnum.ANTHROPIC

    @property
    def default_model(self) -> str:
        """Return the default model for Anthropic."""
        return self._default_model

    def _get_headers(self) -> dict[str, str]:
        """Get Anthropic-specific headers."""
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

    async def _make_request(self, request: LLMRequest) -> dict[str, Any]:
        """Make a messages request to Anthropic."""
        client = await self.get_client()

        # Anthropic has a different message format - system is separate
        system_content = None
        messages = []
        for m in request.messages:
            if m.role == MessageRole.SYSTEM:
                system_content = m.content
            else:
                messages.append({"role": m.role.value, "content": m.content})

        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1024,
            "temperature": request.temperature,
            "top_p": request.top_p,
        }

        if system_content:
            payload["system"] = system_content

        try:
            response = await client.post("/messages", json=payload)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Anthropic rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                )

            if response.status_code in (401, 403):
                raise ProviderAuthError(f"Anthropic authentication failed: {response.text}")

            if response.status_code >= 500:
                raise ProviderServerError(
                    f"Anthropic server error: {response.text}",
                    status_code=response.status_code,
                )

            if response.status_code != 200:
                raise ProviderError(
                    f"Anthropic API error: {response.text}",
                    status_code=response.status_code,
                )

            result: dict[str, Any] = response.json()
            return result

        except httpx.TimeoutException as e:
            raise ProviderError(f"Anthropic request timeout: {e}") from e
        except httpx.RequestError as e:
            raise ProviderError(f"Anthropic request failed: {e}") from e

    def _parse_response(
        self,
        raw_response: dict[str, Any],
        latency_ms: float,
    ) -> LLMResponse:
        """Parse Anthropic's response into unified schema."""
        # Anthropic returns content as a list of content blocks
        content_blocks = raw_response.get("content", [])
        content = ""
        for block in content_blocks:
            if block.get("type") == "text":
                content += block.get("text", "")

        usage_data = raw_response.get("usage")
        usage = None
        if usage_data:
            usage = UsageInfo(
                prompt_tokens=usage_data.get("input_tokens", 0),
                completion_tokens=usage_data.get("output_tokens", 0),
                total_tokens=(
                    usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
                ),
            )

        return LLMResponse(
            id=raw_response.get("id", ""),
            provider=self.provider_name,
            model=raw_response.get("model", self.default_model),
            content=content,
            finish_reason=raw_response.get("stop_reason"),
            usage=usage,
            created_at=datetime.utcnow(),
            latency_ms=latency_ms,
            raw_response=raw_response,
        )


def get_provider(
    provider: LLMProviderEnum,
    api_key: str | None = None,
    model: str | None = None,
) -> BaseLLMProvider:
    """
    Factory function to get a provider instance.

    Args:
        provider: The provider type to instantiate.
        api_key: Optional API key override.
        model: Optional model override.

    Returns:
        BaseLLMProvider: The configured provider instance.

    Raises:
        ValueError: If provider type is unknown.
    """
    if provider == LLMProviderEnum.PERPLEXITY:
        return PerplexityProvider(
            api_key=api_key,
            model=model or PerplexityProvider.MODEL_SONAR_DEEP_RESEARCH,
        )
    elif provider == LLMProviderEnum.OPENAI:
        return OpenAIProvider(
            api_key=api_key,
            model=model or OpenAIProvider.MODEL_GPT5_2,
        )
    elif provider == LLMProviderEnum.ANTHROPIC:
        return AnthropicProvider(
            api_key=api_key,
            model=model or AnthropicProvider.MODEL_CLAUDE_45_SONNET,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
