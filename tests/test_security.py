"""Tests for security utilities: password hashing, JWT tokens, blacklisting, API keys."""

import pytest

from backend.app.core.security import (
    blacklist_all_user_tokens,
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    generate_api_key,
    get_api_key_prefix,
    get_password_hash,
    is_token_blacklisted,
    is_token_revoked_by_global,
    verify_api_key,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "my-secret-password"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct-password")
        assert not verify_password("wrong-password", hashed)


class TestAccessToken:
    def test_create_and_decode(self):
        data = {"user_id": "test-123", "email": "test@example.com"}
        token = create_access_token(data=data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["user_id"] == "test-123"
        assert payload["type"] == "access"

    def test_token_has_jti_and_iat(self):
        token = create_access_token(data={"user_id": "test-123"})
        payload = decode_access_token(token)
        assert payload is not None
        assert "jti" in payload
        assert "iat" in payload

    def test_unique_jti_per_token(self):
        t1 = create_access_token(data={"user_id": "test-123"})
        t2 = create_access_token(data={"user_id": "test-123"})
        p1 = decode_access_token(t1)
        p2 = decode_access_token(t2)
        assert p1["jti"] != p2["jti"]

    def test_custom_type_preserved(self):
        """Tokens with custom type (e.g. email_verification) should not be overwritten."""
        token = create_access_token(data={"user_id": "test-123", "type": "email_verification"})
        # decode_access_token checks type == "access", so it should return None
        assert decode_access_token(token) is None

        # But raw decode should show the custom type
        from jose import jwt

        from backend.app.core.security import ALGORITHM, get_secret_key

        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        assert payload["type"] == "email_verification"


class TestRefreshToken:
    def test_create_and_decode(self):
        token = create_refresh_token(data={"user_id": "test-456"})
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload["user_id"] == "test-456"
        assert payload["type"] == "refresh"

    def test_refresh_token_has_jti(self):
        token = create_refresh_token(data={"user_id": "test-456"})
        payload = decode_refresh_token(token)
        assert "jti" in payload

    def test_access_token_not_decoded_as_refresh(self):
        token = create_access_token(data={"user_id": "test-789"})
        assert decode_refresh_token(token) is None


class TestTokenBlacklisting:
    @pytest.mark.asyncio
    async def test_blacklist_and_check(self, mock_redis):  # noqa: ARG002
        await blacklist_token("jti-abc", 900)
        assert await is_token_blacklisted("jti-abc")

    @pytest.mark.asyncio
    async def test_non_blacklisted_token(self, mock_redis):  # noqa: ARG002
        assert not await is_token_blacklisted("jti-xyz")

    @pytest.mark.asyncio
    async def test_revoke_all_sessions(self, mock_redis):  # noqa: ARG002
        await blacklist_all_user_tokens("user-123")
        # Token issued before revocation should be revoked
        assert await is_token_revoked_by_global("user-123", 0.0)

    @pytest.mark.asyncio
    async def test_token_after_revocation_is_valid(self, mock_redis):  # noqa: ARG002
        import time

        await blacklist_all_user_tokens("user-456")
        # Token issued after revocation should be valid
        future_iat = time.time() + 10
        assert not await is_token_revoked_by_global("user-456", future_iat)


class TestApiKey:
    def test_generate_api_key(self):
        raw, hashed = generate_api_key()
        assert raw.startswith("sk_live_")
        assert verify_api_key(raw, hashed)

    def test_prefix_matches_key_start(self):
        raw, _ = generate_api_key()
        prefix = get_api_key_prefix(raw)
        assert raw.startswith(prefix[:-3])  # Remove trailing "..."
        assert prefix.endswith("...")
