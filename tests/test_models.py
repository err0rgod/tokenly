import pytest
from tokenly.model.models import userdata, jwt_blacklist, refreshSession
from datetime import datetime

def test_userdata_creation():
    """Test the creation of a userdata object."""
    user = userdata(
        user_id="test-123",
        user_name="testuser",
        password="hashedpassword"
    )
    assert user.user_id == "test-123"
    assert user.user_name == "testuser"
    assert user.failed_attempts == 0

def test_jwt_blacklist_creation():
    """Test the creation of a jwt_blacklist object."""
    blacklist = jwt_blacklist(
        user_name="testuser",
        jti="uuid-token-id",
        expired_at=datetime.now()
    )
    assert blacklist.jti == "uuid-token-id"

def test_refresh_session_creation():
    """Test the creation of a refreshSession object."""
    session = refreshSession(
        session_id="sess-123",
        user_id="test-123",
        token_hash="hashabc",
        expires_at=datetime.now()
    )
    assert session.session_id == "sess-123"
    assert session.revoked is False
