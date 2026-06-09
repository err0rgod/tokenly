import pytest
from tokenly_auth import TokenHandler, SessionManager

def test_jwt_creation_and_verification():
    """Test creating and verifying a JWT."""
    handler = TokenHandler(SECRET_KEY="test_secret")
    sub = "user_123"
    
    tokens = handler.createJwt(sub=sub)
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "refresh_days" in tokens
    
    # Verify the access token
    payload = handler.verifyJwt(tokens["access_token"])
    assert payload["sub"] == sub
    assert "jti" in payload


def test_jwt_verification_failure():
    """Test that verification fails for invalid tokens."""
    handler = TokenHandler(SECRET_KEY="test_secret")
    
    with pytest.raises(ValueError, match="Invalid Token"):
        handler.verifyJwt("invalid.token.string")


def test_refresh_token_hashing():
    """Test hashing a refresh token."""
    manager = SessionManager()
    raw_token = "some_random_string"
    
    token_hash = manager.hash_refresh_token(raw_token)
    
    assert token_hash is not None
    assert len(token_hash) == 64  # SHA256 hex digest length
    # Verify it's deterministic
    assert token_hash == manager.hash_refresh_token(raw_token)
