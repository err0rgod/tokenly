import pytest
from tokenly_auth import Security


def test_password_hashing():
    """Test that passwords are hashed correctly."""
    plain = "SecurePassword123!"
    # The new hash_password takes (password, user_id=None)
    hashed = Security["hash"](plain)
    
    assert hashed != plain
    assert hashed.startswith("$argon2")


def test_password_verification_success():
    """Test successful password verification."""
    plain = "SecurePassword123!"
    hashed = Security["hash"](plain)

    # verifyPassword(password, hash, user_id, locked_until, failed_attempts)
    assert Security["verify"](plain, hashed) is True


def test_password_verification_failure():
    """Test failed password verification."""
    plain = "SecurePassword123!"
    hashed = Security["hash"](plain)

    assert Security["verify"]("WrongPassword", hashed) is False


def test_password_reset():
    """Test the password reset utility."""
    old_plain = "OldPassword123!"
    new_plain = "NewPassword123!"
    old_hash = Security["hash"](old_plain)
    
    # reset(old_hash, old_password_plain, new_password, user_id=None)
    new_hash = Security["reset"](old_hash, old_plain, new_plain)
    
    assert new_hash != old_hash
    assert Security["verify"](new_plain, new_hash) is True
    assert Security["verify"](old_plain, new_hash) is False
