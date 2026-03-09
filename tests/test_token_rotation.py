"""Integration tests for token rotation and replay detection."""

import pytest

from backend.app.core.security import (
    blacklist_all_user_tokens,
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    is_token_blacklisted,
    is_token_revoked_by_global,
)


class TestTokenRotation:
    @pytest.mark.asyncio
    async def test_refresh_token_consumed_then_blacklisted(self, mock_redis):  # noqa: ARG002
        """Simulates the refresh flow: old refresh token is consumed and blacklisted."""
        token = create_refresh_token(data={"user_id": "user-1"})
        payload = decode_refresh_token(token)
        jti = payload["jti"]

        # Simulate consuming the refresh token
        await blacklist_token(jti, 7 * 86400)

        # The old refresh token should now be blacklisted
        assert await is_token_blacklisted(jti)

    @pytest.mark.asyncio
    async def test_replay_detection_triggers_global_revoke(self, mock_redis):  # noqa: ARG002
        """If a consumed refresh token is reused, all sessions should be revoked."""
        token = create_refresh_token(data={"user_id": "user-2"})
        payload = decode_refresh_token(token)
        jti = payload["jti"]

        # First use: consume the token
        await blacklist_token(jti, 7 * 86400)

        # Second use: replay detected
        assert await is_token_blacklisted(jti)

        # Revoke all sessions
        await blacklist_all_user_tokens("user-2")

        # All old tokens should be revoked
        assert await is_token_revoked_by_global("user-2", payload["iat"])


class TestGlobalRevocation:
    @pytest.mark.asyncio
    async def test_access_token_revoked_after_global_revoke(self, mock_redis):  # noqa: ARG002
        """Access tokens issued before global revocation should be rejected."""
        token = create_access_token(data={"user_id": "user-3", "email": "test@test.com"})
        from backend.app.core.security import decode_access_token

        payload = decode_access_token(token)
        iat = payload["iat"]

        # Revoke all sessions
        await blacklist_all_user_tokens("user-3")

        # Token issued before revocation should be revoked
        assert await is_token_revoked_by_global("user-3", iat)

    @pytest.mark.asyncio
    async def test_new_token_valid_after_global_revoke(self, mock_redis):  # noqa: ARG002
        """Tokens issued after global revocation should still work."""
        import asyncio

        await blacklist_all_user_tokens("user-4")
        await asyncio.sleep(0.01)  # Ensure time advances

        # New token issued after revocation
        token = create_access_token(data={"user_id": "user-4", "email": "test@test.com"})
        from backend.app.core.security import decode_access_token

        payload = decode_access_token(token)

        # Should NOT be revoked
        assert not await is_token_revoked_by_global("user-4", payload["iat"])
