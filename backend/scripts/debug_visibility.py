import asyncio
import sys
from uuid import UUID
from pathlib import Path

# Add backend to path
sys.path.append(str(Path("/Users/hamid/Documents/ai-visibility")))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.app.core.config import get_settings
from backend.app.repositories.experiment_repo import ExperimentRepository, BatchRunRepository
from backend.app.builders.analysis import AnalysisBuilder
from backend.app.schemas.runner import BatchResult, IterationResult, IterationStatus
from backend.app.schemas.llm import LLMResponse, UsageInfo as Usage
# Import models to ensure relationships are registered
from backend.app.models.user import User
from backend.app.models.experiment import Experiment, BatchRun, Iteration

async def debug_analysis(experiment_id_str: str):
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url))
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        exp_repo = ExperimentRepository(session)
        batch_repo = BatchRunRepository(session)

        # 1. Fetch Experiment
        print(f"Fetching experiment {experiment_id_str}...")
        
        # We need to defer columns that might not exist in the DB due to migration mismatch
        # The error showed: is_recurring, frequency, next_run_at, last_run_at
        from sqlalchemy.orm import defer
        from sqlalchemy import select
        
        # Manually constructing the query with options to avoid the convenience method which might be too eager/rigid
        stmt = (
            select(Experiment)
            .where(Experiment.id == UUID(experiment_id_str))
            .options(
                defer(Experiment.is_recurring),
                defer(Experiment.frequency),
                defer(Experiment.next_run_at),
                defer(Experiment.last_run_at)
            )
        )
        # We still need the relationships though, let's try to rely on lazy loading or simple eager load
        # But get_experiment_with_results uses selectinload, so let's try to mimic that but with defers
        from sqlalchemy.orm import selectinload
        stmt = stmt.options(
             selectinload(Experiment.batch_runs).selectinload(BatchRun.iterations)
        )
        
        result = await session.execute(stmt)
        experiment = result.scalar_one_or_none()
        if not experiment:
            print("Experiment not found!")
            return

        print(f"Target Brand: '{experiment.target_brand}'")
        
        if not experiment.batch_runs:
            print("No batch runs found.")
            return

        batch_run = experiment.batch_runs[0]
        print(f"Batch Run ID: {batch_run.id}")
        
        # 2. Reconstruct BatchResult object for the analyzer
        # We need to convert DB iterations back to Schema objects
        iterations = []
        for db_iter in batch_run.iterations:
            result = IterationResult(
                iteration_index=db_iter.iteration_index,
                status=IterationStatus(db_iter.status),
                response=LLMResponse(
                    id="debug-id",
                    provider=batch_run.provider,
                    model=batch_run.model,
                    content=db_iter.raw_response,
                    usage=Usage(
                        prompt_tokens=0, # Dummies
                        completion_tokens=0,
                        total_tokens=0
                    )
                ) if db_iter.raw_response else None,
                latency_ms=db_iter.latency_ms,
                error_message=db_iter.error_message
            )
            iterations.append(result)
            
            # Print a snippet of the response to verify content
            snippet = db_iter.raw_response[:100] if db_iter.raw_response else "NONE"
            print(f"-- Iteration {db_iter.iteration_index}: {snippet}...")
            if experiment.target_brand.lower() in (db_iter.raw_response or "").lower():
                print(f"   [MATCH FOUND] Brand '{experiment.target_brand}' found in text (simple string check).")
            else:
                print(f"   [NO MATCH] Brand '{experiment.target_brand}' NOT found in text.")

        batch_result = BatchResult(
            batch_id=batch_run.id,
            provider=batch_run.provider,
            model=batch_run.model,
            prompt=experiment.prompt,
            config=batch_run.config if hasattr(batch_run, 'config') else {},
            total_iterations=len(iterations),
            successful_iterations=len([i for i in iterations if i.status == IterationStatus.SUCCESS]),
            failed_iterations=len([i for i in iterations if i.status == IterationStatus.FAILED]),
            total_duration_ms=0,
            iterations=iterations,
            metrics={}
        )

        # 3. Run Analyzer
        print("\nRunning AnalysisBuilder...")
        analyzer = AnalysisBuilder()
        
        target_brands = [experiment.target_brand]
        if experiment.competitor_brands:
            target_brands.extend(experiment.competitor_brands)
            
        analysis_result = analyzer.analyze_batch(
            batch_result=batch_result,
            target_brands=target_brands
        )

        # 4. Print Results
        print("\n--- Analysis Results ---")
        metrics = analysis_result.raw_metrics
        # print(f"Metrics: {metrics}")
        
        target_vis = metrics.get('target_visibility', {})
        print(f"Target Visibility Rate: {target_vis.get('visibility_rate')}")
        
        print("\nIf 'Target Visibility Rate' is 0.0 but [MATCH FOUND] was printed above, the Regex logic in AnalysisBuilder is likely too strict.")

    await engine.dispose()

if __name__ == "__main__":
    # ID from browser walkthrough
    EXP_ID = "99208e6b-06d6-4564-b398-ec27a1972e35" 
    asyncio.run(debug_analysis(EXP_ID))
