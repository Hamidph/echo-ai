
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import asyncio
from datetime import datetime, timezone
from backend.app.routers.experiments import get_experiment_detail, create_experiment, ExperimentRequest
from backend.app.models.experiment import ExperimentStatus
from backend.app.models.user import User
from backend.app.core.security import get_secret_key
from backend.app.builders.providers import OpenAIProvider, ProviderServerError
from backend.app.schemas.llm import LLMRequest, Message, MessageRole, LLMProvider
from fastapi import status, HTTPException

class TestAuditFixes(unittest.IsolatedAsyncioTestCase):

    async def test_crit1_auth_check_ownership(self):
        """Verify that get_experiment_detail verifies ownership."""
        mock_session = AsyncMock()
        mock_exp_repo = AsyncMock()
        
        user_a_id = uuid.uuid4()
        user_b_id = uuid.uuid4()
        current_user = User(id=user_a_id, email="a@example.com", is_active=True)
        
        experiment_id = uuid.uuid4()

        with patch("backend.app.routers.experiments.ExperimentRepository", return_value=mock_exp_repo):
            # Scenario 1: User A owns the experiment (Should Pass)
            valid_exp = MagicMock()
            valid_exp.id = experiment_id
            valid_exp.user_id = user_a_id
            valid_exp.prompt = "Test prompt"
            valid_exp.target_brand = "BrandX"
            valid_exp.status = "pending"
            valid_exp.error_message = None
            valid_exp.created_at = datetime.now(timezone.utc)
            valid_exp.updated_at = datetime.now(timezone.utc)
            valid_exp.batch_runs = []
            valid_exp.competitor_brands = []
            valid_exp.domain_whitelist = []
            valid_exp.config = {}
            valid_exp.is_recurring = False
            valid_exp.frequency = None
            valid_exp.next_run_at = None
            valid_exp.last_run_at = None

            mock_exp_repo.get_experiment_by_user.return_value = valid_exp
            mock_exp_repo.get_experiment_with_results.return_value = valid_exp
            
            await get_experiment_detail(experiment_id, mock_session, current_user)
            mock_exp_repo.get_experiment_by_user.assert_called_with(experiment_id, user_a_id)

            # Scenario 2: User A tries to access User B's experiment (Should Fail)
            mock_exp_repo.get_experiment_by_user.return_value = None
            
            with self.assertRaises(HTTPException) as cm:
                await get_experiment_detail(experiment_id, mock_session, current_user)
            self.assertEqual(cm.exception.status_code, status.HTTP_404_NOT_FOUND)

    async def test_crit2_quota_rollback(self):
        """Verify that if Celery task fails to queue, user quota is refunded."""
        mock_session = AsyncMock()
        mock_exp_repo = AsyncMock()
        
        user_id = uuid.uuid4()
        current_user = User(
            id=user_id, 
            email="test@example.com", 
            monthly_prompt_quota=100,
            prompts_used_this_month=50 
        )
        
        request = ExperimentRequest(
            prompt="Test prompt for verification",
            target_brand="TestBrand",
            competitor_brands=["B"],
            iterations=10, 
            provider=LLMProvider.OPENAI
        )
        
        mock_exp = MagicMock(id=uuid.uuid4())
        mock_exp_repo.create_experiment.return_value = mock_exp
        
        # Mock Request object for rate limiter
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # Patch get_settings because it is called inside create_experiment
        with patch("backend.app.routers.experiments.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.testing_mode = False
            mock_settings.unlimited_prompts = False
            # Ensure max_iterations is high enough
            mock_settings.max_iterations = 100 
            mock_get_settings.return_value = mock_settings
            
            with patch("backend.app.routers.experiments.ExperimentRepository", return_value=mock_exp_repo):
                with patch("backend.app.routers.experiments.execute_experiment_task") as mock_task:
                    mock_task.delay.side_effect = Exception("Redis Down")
                    
                    with self.assertRaises(HTTPException) as cm:
                        await create_experiment(request, mock_request, mock_session, current_user)
                    
                    self.assertEqual(cm.exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
                    # Quota logic: 50 + 10 = 60 (commit) -> fail -> 60 - 10 = 50 (commit)
                    self.assertEqual(current_user.prompts_used_this_month, 50)
                    
                    mock_exp_repo.update_experiment_status.assert_called_with(
                        mock_exp.id, 
                        ExperimentStatus.FAILED, 
                        error_message="System overloaded, please try again later."
                    )

    def test_high4_secret_key_security(self):
        """Verify get_secret_key raises error if insecure default is used in production."""
        with patch("backend.app.core.security.settings") as mock_settings:
            # Case 1: Testing Mode = True
            mock_settings.testing_mode = True
            mock_settings.secret_key = 'your-secret-key-change-in-production'
            self.assertEqual(get_secret_key(), 'your-secret-key-change-in-production')
            
            # Case 2: Production Mode + Default Key
            mock_settings.testing_mode = False
            mock_settings.secret_key = 'your-secret-key-change-in-production'
            with self.assertRaisesRegex(ValueError, "FATAL: Insecure SECRET_KEY"):
                get_secret_key()
                
            # Case 3: Production Mode + Secure Key
            mock_settings.testing_mode = False
            mock_settings.secret_key = 'secure-random-key'
            self.assertEqual(get_secret_key(), 'secure-random-key')

    async def test_high3_provider_retries(self):
        """Verify OpenAIProvider retries on 500 errors."""
        provider = OpenAIProvider(api_key="sk-test")
        
        mock_client = AsyncMock()
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        mock_response_500.text = "Server Error"
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "id": "1",
            "model": "gpt-4o",
            "output": [{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Success"}]}],
            "usage": {"total_tokens": 10}
        }
        
        # Side effect: Fail twice with 500, then succeed
        mock_client.post.side_effect = [
            mock_response_500, 
            mock_response_500, 
            mock_response_200
        ]
        
        with patch.object(provider, 'get_client', return_value=mock_client):
            request = LLMRequest(messages=[Message(role=MessageRole.USER, content="Hi")])
            response = await provider.generate(request)
            
            self.assertEqual(response.content, "Success")
            self.assertEqual(mock_client.post.call_count, 3)

if __name__ == "__main__":
    unittest.main()
