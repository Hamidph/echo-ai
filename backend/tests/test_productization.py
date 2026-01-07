
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
import os

# Set dummy env vars to satisfy config
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

# Import routers after setting env vars
from backend.app.routers.demo import router as demo_router
from backend.app.routers.health import router as health_router
from backend.app.models.demo import DemoUsage
from backend.app.schemas.llm import LLMProvider
from fastapi import Request
from backend.app.routers.health import router as health_router
from backend.app.models.demo import DemoUsage
from backend.app.schemas.llm import LLMProvider

class TestProductization(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        self.app.include_router(demo_router)
        self.app.include_router(health_router)
        self.client = TestClient(self.app)
        
        # Mock DB Session
        self.mock_session = AsyncMock()
        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.execute = AsyncMock()
        
        # Patch dependency injection for DbSession
        # In a real integration test we'd override_dependency, but for unit test patching is easier if we can target where it's used
        # Since we are testing the router functions directly often, or via client if we can override deps.
        # Let's try to patch the `session` argument injection or just mock the internals.
        
    @patch("backend.app.routers.health.get_settings")
    @patch("backend.app.routers.health.Redis")
    async def test_health_detailed(self, mock_redis_cls, mock_get_settings):
        # Setup Mocks
        mock_settings = MagicMock()
        mock_settings.redis_url = "redis://localhost:6379/0"
        mock_get_settings.return_value = mock_settings
        
        mock_redis = AsyncMock()
        mock_redis_cls.from_url.return_value = mock_redis
        
        # Test Function directly (bypassing FastAPI dep injection for simplicity in unit test)
        from backend.app.routers.health import detailed_health_check
        
        # 1. Healthy Case
        self.mock_session.execute.return_value.scalar.return_value = 1
        response = await detailed_health_check(self.mock_session)
        self.assertEqual(response["status"], "healthy")
        self.assertEqual(response["components"]["database"], "healthy")
        self.assertEqual(response["components"]["redis"], "healthy")
        
    @patch("backend.app.routers.demo.RunnerBuilder")
    @patch("backend.app.routers.demo.AnalysisBuilder")
    @patch("backend.app.routers.demo.get_settings")
    async def test_demo_quick_analysis(self, mock_settings, mock_analysis_builder_cls, mock_runner_builder_cls):
        from backend.app.routers.demo import run_quick_demo, DemoRequest
        
        # Setup Mocks
        mock_runner = AsyncMock()
        mock_runner_builder_cls.return_value = mock_runner
        
        # Mock Batch Result
        mock_batch_result = MagicMock()
        mock_batch_result.iterations = [] # Empty for simplicity
        mock_runner.run_batch.return_value = mock_batch_result
        
        # Mock Analysis Result
        mock_analyzer = MagicMock()
        mock_analysis_builder_cls.return_value = mock_analyzer
        mock_analysis_result = MagicMock()
        mock_analysis_result.raw_metrics = {
            "Test Brand": {
                "visibility_score": 80.0,
                "share_of_voice": 50.0,
                "sentiment_score": 0.8
            }
        }
        mock_analyzer.analyze_batch.return_value = mock_analysis_result
        
        # Test Request - Use real Request for slowapi compatibility
        scope = {"type": "http", "client": ("127.0.0.1", 8000), "method": "POST", "path": "/demo", "headers": []}
        req_obj = Request(scope)
        
        demo_req = DemoRequest(
            prompt="What is Test Brand?",
            target_brand="Test Brand",
            provider=LLMProvider.OPENAI
        )
        
        # Execute
        response = await run_quick_demo(req_obj, demo_req, self.mock_session)
        
        # Verify Response
        self.assertEqual(response.visibility_score, 80.0)
        self.assertEqual(response.share_of_voice, 50.0)
        
        # Verify DB Interaction (Analytics)
        self.mock_session.add.assert_called_once()
        args, _ = self.mock_session.add.call_args
        self.assertIsInstance(args[0], DemoUsage)
        self.assertEqual(args[0].target_brand, "Test Brand")

if __name__ == "__main__":
    unittest.main()
