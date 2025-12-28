"""
AnalysisBuilder - The Statistical Analysis Engine.

This module implements the core analytics logic for computing visibility
metrics from probabilistic batch results.

Innovation: This is the "brain" of the Probabilistic Visibility Engine.
By analyzing N iterations of the same prompt, we compute metrics that
single-shot tools cannot provide:
- Visibility Rate: How often a brand appears across iterations
- Share of Voice: Brand frequency vs competitors
- Consistency Score: Response similarity using fuzzy matching
- Hallucination Rate: Citation validity for grounded responses

These metrics create a new category of data: "Generative Risk Analytics".
"""

import re
from dataclasses import dataclass
from typing import Any

from rapidfuzz import fuzz

from backend.app.schemas.llm import LLMProvider, PerplexityResponse
from backend.app.schemas.runner import BatchResult, IterationStatus


@dataclass
class BrandMention:
    """
    Represents a brand mention in an LLM response.

    Attributes:
        brand: The brand name that was mentioned.
        count: Number of times mentioned in the response.
        position: First character position of mention (for ranking).
        context: Surrounding text snippet for context.
    """

    brand: str
    count: int
    position: int
    context: str


@dataclass
class VisibilityMetrics:
    """
    Visibility analysis results for a single brand.

    Innovation: These metrics quantify brand presence in LLM responses,
    enabling data-driven decisions about AI visibility strategy.

    Attributes:
        brand: The brand being analyzed.
        mention_count: Total mentions across all iterations.
        visibility_rate: Proportion of iterations mentioning the brand (0-1).
        avg_mentions_per_response: Average mentions when present.
        first_mention_rate: Rate at which brand appears first.
        avg_position: Average character position of first mention.
    """

    brand: str
    mention_count: int
    visibility_rate: float
    avg_mentions_per_response: float
    first_mention_rate: float
    avg_position: float | None


@dataclass
class ShareOfVoice:
    """
    Share of Voice analysis comparing multiple brands.

    Innovation: Share of Voice enables competitive analysis by measuring
    relative brand visibility in LLM recommendations.

    Attributes:
        brand: The brand being analyzed.
        share: Proportion of total brand mentions (0-1).
        rank: Rank among all analyzed brands (1 = most visible).
    """

    brand: str
    share: float
    rank: int


@dataclass
class ConsistencyMetrics:
    """
    Response consistency analysis.

    Innovation: Consistency metrics reveal LLM reliability. High variance
    indicates the model gives different answers to the same question,
    which is a risk factor for brand visibility strategies.

    Attributes:
        avg_similarity: Average pairwise similarity (0-100).
        min_similarity: Minimum pairwise similarity.
        max_similarity: Maximum pairwise similarity.
        std_deviation: Standard deviation of similarities.
        consistency_score: Normalized score (0-1, higher = more consistent).
    """

    avg_similarity: float
    min_similarity: float
    max_similarity: float
    std_deviation: float
    consistency_score: float


@dataclass
class HallucinationMetrics:
    """
    Hallucination detection results.

    Innovation: For Perplexity responses with citations, we can verify
    if cited sources are from trusted domains. This enables "Generative
    Risk Analytics" by quantifying citation reliability.

    Attributes:
        total_citations: Total citations across all iterations.
        valid_citations: Citations from whitelisted domains.
        invalid_citations: Citations from non-whitelisted domains.
        hallucination_rate: Proportion of invalid citations (0-1).
        flagged_urls: List of URLs not in whitelist.
    """

    total_citations: int
    valid_citations: int
    invalid_citations: int
    hallucination_rate: float
    flagged_urls: list[str]


@dataclass
class AnalysisResult:
    """
    Complete analysis results for a batch run.

    Innovation: This comprehensive result object enables the "Probabilistic
    Visibility Report" - a data product that provides statistically significant
    insights into brand visibility across LLM providers.

    Attributes:
        batch_id: The analyzed batch identifier.
        provider: LLM provider used.
        model: Model used.
        total_responses: Number of successful responses analyzed.
        target_visibility: Visibility metrics for the target brand.
        competitor_visibility: Visibility metrics for competitors.
        share_of_voice: Share of Voice analysis.
        consistency: Response consistency metrics.
        hallucination: Hallucination detection results (if applicable).
        raw_metrics: Dictionary of all metrics for storage.
    """

    batch_id: str
    provider: str
    model: str
    total_responses: int
    target_visibility: VisibilityMetrics | None
    competitor_visibility: list[VisibilityMetrics]
    share_of_voice: list[ShareOfVoice]
    consistency: ConsistencyMetrics
    hallucination: HallucinationMetrics | None
    raw_metrics: dict[str, Any]


class AnalysisBuilder:
    """
    The Statistical Analysis Engine for probabilistic visibility analysis.

    This builder processes BatchResult data to compute visibility metrics,
    consistency scores, and hallucination rates.

    Innovation: The AnalysisBuilder transforms raw LLM responses into
    actionable intelligence. By applying statistical analysis to N iterations,
    we create metrics that quantify the inherent randomness in LLM outputs.
    This is the core value proposition for the Innovator Founder Visa.
    """

    def __init__(self) -> None:
        """Initialize the AnalysisBuilder."""
        # Compile regex patterns for efficiency
        self._word_boundary_pattern = r"\b{}\b"

    def analyze_batch(
        self,
        batch_result: BatchResult,
        target_brands: list[str],
        domain_whitelist: list[str] | None = None,
    ) -> AnalysisResult:
        """
        Perform complete analysis on a batch result.

        This is the main entry point for analysis. It computes all metrics
        including visibility, share of voice, consistency, and hallucination.

        Innovation: This method orchestrates the full "Probabilistic Visibility
        Analysis" pipeline, transforming raw responses into business intelligence.

        Args:
            batch_result: The batch execution results.
            target_brands: List of brands to analyze (first is primary target).
            domain_whitelist: Optional list of trusted domains for hallucination check.

        Returns:
            AnalysisResult: Complete analysis with all metrics.
        """
        responses = batch_result.raw_responses
        total_responses = len(responses)

        if total_responses == 0:
            # Return empty results if no successful responses
            return self._empty_result(batch_result)

        # Compute visibility for all brands
        all_visibility: list[VisibilityMetrics] = []
        for brand in target_brands:
            visibility = self._compute_visibility(responses, brand)
            all_visibility.append(visibility)

        # Separate target and competitor visibility
        target_visibility = all_visibility[0] if all_visibility else None
        competitor_visibility = all_visibility[1:] if len(all_visibility) > 1 else []

        # Compute Share of Voice
        share_of_voice = self._compute_share_of_voice(all_visibility)

        # Compute Consistency Score
        consistency = self._compute_consistency(responses)

        # Compute Hallucination metrics (Perplexity only)
        hallucination = None
        if batch_result.provider == LLMProvider.PERPLEXITY and domain_whitelist:
            hallucination = self._compute_hallucination(
                batch_result.iterations,
                domain_whitelist,
            )

        # Build raw metrics dictionary for storage
        raw_metrics = self._build_raw_metrics(
            target_visibility=target_visibility,
            competitor_visibility=competitor_visibility,
            share_of_voice=share_of_voice,
            consistency=consistency,
            hallucination=hallucination,
            total_responses=total_responses,
        )

        return AnalysisResult(
            batch_id=str(batch_result.batch_id),
            provider=batch_result.provider.value,
            model=batch_result.model,
            total_responses=total_responses,
            target_visibility=target_visibility,
            competitor_visibility=competitor_visibility,
            share_of_voice=share_of_voice,
            consistency=consistency,
            hallucination=hallucination,
            raw_metrics=raw_metrics,
        )

    def _compute_visibility(
        self,
        responses: list[str],
        brand: str,
    ) -> VisibilityMetrics:
        """
        Compute visibility metrics for a single brand.

        Innovation: Uses regex with word boundaries for accurate brand detection,
        avoiding false positives from partial matches.

        Args:
            responses: List of LLM response texts.
            brand: Brand name to search for.

        Returns:
            VisibilityMetrics: Computed visibility metrics.
        """
        # Create case-insensitive pattern with word boundaries
        pattern = re.compile(
            self._word_boundary_pattern.format(re.escape(brand)),
            re.IGNORECASE,
        )

        total_mentions = 0
        responses_with_mention = 0
        first_mentions = 0
        positions: list[int] = []

        for response in responses:
            matches = list(pattern.finditer(response))

            if matches:
                responses_with_mention += 1
                total_mentions += len(matches)

                # Track position of first mention
                first_pos = matches[0].start()
                positions.append(first_pos)

                # Check if this brand appears first among all brands
                # (simplified: just check if it's in first 100 chars)
                if first_pos < 100:
                    first_mentions += 1

        total_responses = len(responses)
        visibility_rate = responses_with_mention / total_responses if total_responses > 0 else 0.0
        avg_mentions = (
            total_mentions / responses_with_mention if responses_with_mention > 0 else 0.0
        )
        first_mention_rate = first_mentions / total_responses if total_responses > 0 else 0.0
        avg_position = sum(positions) / len(positions) if positions else None

        return VisibilityMetrics(
            brand=brand,
            mention_count=total_mentions,
            visibility_rate=visibility_rate,
            avg_mentions_per_response=avg_mentions,
            first_mention_rate=first_mention_rate,
            avg_position=avg_position,
        )

    def _compute_share_of_voice(
        self,
        visibility_metrics: list[VisibilityMetrics],
    ) -> list[ShareOfVoice]:
        """
        Compute Share of Voice for all analyzed brands.

        Innovation: Share of Voice provides competitive intelligence by
        measuring relative visibility across brands.

        Args:
            visibility_metrics: Visibility metrics for all brands.

        Returns:
            List of ShareOfVoice results sorted by share.
        """
        total_mentions = sum(v.mention_count for v in visibility_metrics)

        if total_mentions == 0:
            return [
                ShareOfVoice(brand=v.brand, share=0.0, rank=i + 1)
                for i, v in enumerate(visibility_metrics)
            ]

        # Calculate share and sort by mentions
        shares: list[tuple[str, float, int]] = []
        for v in visibility_metrics:
            share = v.mention_count / total_mentions
            shares.append((v.brand, share, v.mention_count))

        # Sort by mentions descending
        shares.sort(key=lambda x: x[2], reverse=True)

        return [
            ShareOfVoice(brand=brand, share=share, rank=i + 1)
            for i, (brand, share, _) in enumerate(shares)
        ]

    def _compute_consistency(
        self,
        responses: list[str],
    ) -> ConsistencyMetrics:
        """
        Compute response consistency using fuzzy string matching.

        Innovation: Uses Levenshtein distance (via rapidfuzz) to measure
        how similar responses are to each other. High variance indicates
        the LLM gives inconsistent answers, which is a risk factor.

        Args:
            responses: List of LLM response texts.

        Returns:
            ConsistencyMetrics: Computed consistency metrics.
        """
        if len(responses) < 2:
            return ConsistencyMetrics(
                avg_similarity=100.0,
                min_similarity=100.0,
                max_similarity=100.0,
                std_deviation=0.0,
                consistency_score=1.0,
            )

        # Compute pairwise similarities
        similarities: list[float] = []

        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                # Use rapidfuzz for fast fuzzy matching
                similarity = fuzz.ratio(responses[i], responses[j])
                similarities.append(similarity)

        # Compute statistics
        avg_similarity = sum(similarities) / len(similarities)
        min_similarity = min(similarities)
        max_similarity = max(similarities)

        # Compute standard deviation
        variance = sum((s - avg_similarity) ** 2 for s in similarities) / len(similarities)
        std_deviation = variance**0.5

        # Normalize to 0-1 score (higher = more consistent)
        # A score of 100 similarity = 1.0, score of 0 = 0.0
        consistency_score = avg_similarity / 100.0

        return ConsistencyMetrics(
            avg_similarity=avg_similarity,
            min_similarity=min_similarity,
            max_similarity=max_similarity,
            std_deviation=std_deviation,
            consistency_score=consistency_score,
        )

    def _compute_hallucination(
        self,
        iterations: list[Any],
        domain_whitelist: list[str],
    ) -> HallucinationMetrics:
        """
        Compute hallucination metrics by validating citations.

        Innovation: For Perplexity responses with citations, we verify
        if cited sources are from trusted domains. This quantifies
        "citation reliability" - a novel metric for AI-generated content.

        Args:
            iterations: List of iteration results.
            domain_whitelist: List of trusted domains.

        Returns:
            HallucinationMetrics: Computed hallucination metrics.
        """
        total_citations = 0
        valid_citations = 0
        flagged_urls: list[str] = []

        # Normalize whitelist domains
        whitelist_normalized = [d.lower().strip() for d in domain_whitelist]

        for iteration in iterations:
            if iteration.status != IterationStatus.SUCCESS:
                continue

            # Check if response has citations (Perplexity-specific)
            response = iteration.response
            if response is None:
                continue

            # Handle PerplexityResponse with search_results
            citations: list[str] = []
            if isinstance(response, PerplexityResponse) and response.search_results:
                citations = [sr.url for sr in response.search_results]
            elif hasattr(response, "raw_response") and response.raw_response:
                # Try to extract from raw response
                raw = response.raw_response
                if isinstance(raw, dict) and "search_results" in raw:
                    citations = [sr.get("url", "") for sr in raw.get("search_results", [])]

            for url in citations:
                if not url:
                    continue

                total_citations += 1

                # Extract domain from URL
                domain = self._extract_domain(url)

                # Check if domain is in whitelist
                if any(w in domain.lower() for w in whitelist_normalized):
                    valid_citations += 1
                else:
                    flagged_urls.append(url)

        invalid_citations = total_citations - valid_citations
        hallucination_rate = invalid_citations / total_citations if total_citations > 0 else 0.0

        return HallucinationMetrics(
            total_citations=total_citations,
            valid_citations=valid_citations,
            invalid_citations=invalid_citations,
            hallucination_rate=hallucination_rate,
            flagged_urls=flagged_urls[:20],  # Limit to 20 examples
        )

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from a URL.

        Args:
            url: Full URL string.

        Returns:
            Domain portion of the URL.
        """
        # Simple domain extraction
        url = url.lower()
        if "://" in url:
            url = url.split("://", 1)[1]
        if "/" in url:
            url = url.split("/", 1)[0]
        return url

    def _build_raw_metrics(
        self,
        target_visibility: VisibilityMetrics | None,
        competitor_visibility: list[VisibilityMetrics],
        share_of_voice: list[ShareOfVoice],
        consistency: ConsistencyMetrics,
        hallucination: HallucinationMetrics | None,
        total_responses: int,
    ) -> dict[str, Any]:
        """
        Build a dictionary of all metrics for database storage.

        Args:
            All computed metrics.

        Returns:
            Dictionary suitable for JSON storage.
        """
        metrics: dict[str, Any] = {
            "total_responses": total_responses,
            "consistency": {
                "avg_similarity": consistency.avg_similarity,
                "min_similarity": consistency.min_similarity,
                "max_similarity": consistency.max_similarity,
                "std_deviation": consistency.std_deviation,
                "consistency_score": consistency.consistency_score,
            },
        }

        if target_visibility:
            metrics["target_visibility"] = {
                "brand": target_visibility.brand,
                "mention_count": target_visibility.mention_count,
                "visibility_rate": target_visibility.visibility_rate,
                "avg_mentions_per_response": target_visibility.avg_mentions_per_response,
                "first_mention_rate": target_visibility.first_mention_rate,
                "avg_position": target_visibility.avg_position,
            }

        if competitor_visibility:
            metrics["competitor_visibility"] = [
                {
                    "brand": v.brand,
                    "mention_count": v.mention_count,
                    "visibility_rate": v.visibility_rate,
                    "avg_mentions_per_response": v.avg_mentions_per_response,
                }
                for v in competitor_visibility
            ]

        if share_of_voice:
            metrics["share_of_voice"] = [
                {"brand": s.brand, "share": s.share, "rank": s.rank} for s in share_of_voice
            ]

        if hallucination:
            metrics["hallucination"] = {
                "total_citations": hallucination.total_citations,
                "valid_citations": hallucination.valid_citations,
                "invalid_citations": hallucination.invalid_citations,
                "hallucination_rate": hallucination.hallucination_rate,
                "flagged_urls": hallucination.flagged_urls,
            }

        return metrics

    def _empty_result(self, batch_result: BatchResult) -> AnalysisResult:
        """
        Create an empty result when no responses are available.

        Args:
            batch_result: The batch result with no successful responses.

        Returns:
            AnalysisResult with zero/empty metrics.
        """
        return AnalysisResult(
            batch_id=str(batch_result.batch_id),
            provider=batch_result.provider.value,
            model=batch_result.model,
            total_responses=0,
            target_visibility=None,
            competitor_visibility=[],
            share_of_voice=[],
            consistency=ConsistencyMetrics(
                avg_similarity=0.0,
                min_similarity=0.0,
                max_similarity=0.0,
                std_deviation=0.0,
                consistency_score=0.0,
            ),
            hallucination=None,
            raw_metrics={"total_responses": 0, "error": "No successful responses"},
        )
