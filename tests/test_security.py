import pytest
from tokenly.model.models import userdata
from tokenly.secure.hashed import hash_password, verifyPassword
from unittest.mock import MagicMock

def test_password_hashing():
    """Test that passwords are hashed and not stored in plain text."""
    user = userdata(
        user_id="u1",
        user_name="user1",
        password="SecurePassword123!"
    )
    hashed_user = hash_password(user)
    assert hashed_user.password != "SecurePassword123!"
    assert hashed_user.password.startswith("$argon2")

def test_password_verification_success():
    """Test successful password verification."""
    plain = "SecurePassword123!"
    user = userdata(
        user_id="u1",
        user_name="user1",
        password="SecurePassword123!"
    )
    hash_password(user)
    
    assert verifyPassword(user, plain) is True
    assert user.failed_attempts == 0

def test_password_verification_failure():
    """Test failed password verification and attempt incrementing."""
    user = userdata(
        user_id="u1",
        user_name="user1",
        password="SecurePassword123!"
    )
    hash_password(user)
    
    assert verifyPassword(user, "WrongPassword") is False
    assert user.failed_attempts == 1

def test_account_locking():
    """Test that account locks after maximum failed attempts."""
    user = userdata(
        user_id="u1",
        user_name="user1",
        password="SecurePassword123!",
        failed_attempts=4
    )
    hash_password(user)
    
    # 5th failed attempt
    verifyPassword(user, "WrongPassword")
    assert user.locked_until is not None
    
    # Try to verify while locked
    with pytest.raises(ValueError, match="Account Locked"):
        verifyPassword(user, "SecurePassword123!")
