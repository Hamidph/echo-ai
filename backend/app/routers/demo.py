
import logging
import asyncio
from typing import Annotated, Any
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.core.database import DbSession
from backend.app.core.config import get_settings
from backend.app.models.demo import DemoUsage
from backend.app.builders.runner import RunnerBuilder, BatchConfig
from backend.app.builders.analysis import AnalysisBuilder
from backend.app.schemas.llm import LLMProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["Demo"])
limiter = Limiter(key_func=get_remote_address)

class DemoRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500)
    target_brand: str = Field(..., min_length=2, max_length=100)
    provider: LLMProvider = Field(default=LLMProvider.OPENAI)

class DemoResponse(BaseModel):
    visibility_score: float
    share_of_voice: float
    sentiment_score: float = 0.0
    citations: list[str] = []
    message: str

@router.post(
    "/quick-analysis",
    response_model=DemoResponse,
    summary="Run a quick 5-iteration public demo analysis",
)
@limiter.limit("5/minute")
async def run_quick_demo(
    request: Request,
    demo_req: DemoRequest,
    session: DbSession,
):
    """
    Public demo endpoint. Runs a small-scale analysis (5 iterations) synchronously.
    
    Current limitations:
    - Max 5 iterations
    - Rate limited to 5 per minute per IP
    - No auth required
    """
    settings = get_settings()
    
    # 1. Log Usage
    client_ip = request.client.host if request.client else "unknown"
    usage_entry = DemoUsage(
        target_brand=demo_req.target_brand,
        provider=demo_req.provider.value,
        prompt=demo_req.prompt,
        ip_address=client_ip
    )
    session.add(usage_entry)
    await session.commit()

    # 2. Configure simplified batch
    # We use a mocked/simplified config for the runner
    batch_config = BatchConfig(
        iterations=5,  # HARD LIMIT
        max_concurrency=5,
        temperature=0.7,
        model=None, # Use provider default
    )
    
    logger.info(f"Running demo analysis for brand '{demo_req.target_brand}' from IP {client_ip}")

    try:
        # 3. Execute Batch (using existing RunnerBuilder)
        # We invoke the runner directly to avoid Celery overhead for this quick interaction
        runner = RunnerBuilder()
        batch_result = await runner.run_batch(
            prompt=demo_req.prompt,
            provider=demo_req.provider,
            config=batch_config,
        )

        # 4. Analyze Results
        analyzer = AnalysisBuilder()
        analysis_result = analyzer.analyze_batch(
            batch_result=batch_result,
            target_brands=[demo_req.target_brand],
        )

        # 5. Extract Metrics
        # raw_metrics is dict like {brand: {visibility_score: ..., sentiment: ...}}
        metrics = analysis_result.raw_metrics.get(demo_req.target_brand, {})
        
        # Extract top citations/snippets (simplified logic)
        citations = []
        for iter in batch_result.iterations:
             if iter.response and iter.response.content:
                 citations.append(iter.response.content[:200] + "...")
        
        return DemoResponse(
            visibility_score=metrics.get("visibility_score", 0.0),
            share_of_voice=metrics.get("share_of_voice", 0.0),
            sentiment_score=metrics.get("sentiment_score", 0.0),
            citations=citations[:3], # Return top 3 snippets
            message="This is a simplified demo result. Sign up for full details."
        )

    except Exception as e:
        logger.error(f"Demo analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Demo analysis service is currently busy. Please try again later."
        )
