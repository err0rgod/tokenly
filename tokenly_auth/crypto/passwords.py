"""
Security module for password hashing and verification.
Uses Argon2 for secure password hashing and provides brute-force protection
by tracking failed attempts and locking accounts temporarily.
"""

from typing import Optional
from argon2 import PasswordHasher
from datetime import datetime, timezone
import logging

# Initializing the password hashing and logging objects
ph = PasswordHasher()
logger = logging.getLogger(__name__)


def hash_password(password: str, user_id: Optional[str] = None) -> str:
    """
    Hashes the user's password using Argon2.

    Args:
        password (str): The plain-text password to hash.
        user_id (str, optional): Optional identifier for logging.

    Returns:
        str: The hashed password.
    """
    if user_id:
        logger.info(f"Hashed password of {user_id}")
    return ph.hash(password)


def verifyPassword(password: str, hash: str, user_id: Optional[str] = None, locked_until: Optional[datetime] = None, failed_attempts: Optional[int] = 0) -> bool:
    """
    Verifies a plain-text password against a stored hash.

    Args:
        password (str): The plain-text password to verify.
        hash (str): The stored Argon2 hash.
        user_id (str, optional): User identifier for logging.
        locked_until (datetime, optional): Current lock status.
        failed_attempts (int, optional): Current failed attempts count (not managed by this utility).

    Returns:
        bool: True if verification succeeds, False otherwise.

    Raises:
        ValueError: If the account is currently locked.
    """
    now = datetime.now(timezone.utc)
    if locked_until and now < locked_until:
        logger.warning(f"account locked of user {user_id}")
        raise ValueError("Account Locked Try again Later.")
    
    try:
        # Argon2 verify expects (hash, password)
        return ph.verify(hash, password)
    except Exception as e:
        logger.warning(f"Verification failed for {user_id}: {str(e)}")
        return False




        

def resetPassword(old_hash: str, old_password_plain: str, new_password: str, user_id: Optional[str] = None) -> str:
    """
    Utility to verify old password and generate a new hash.

    Args:
        old_hash (str): Current stored password hash.
        old_password_plain (str): Current plain-text password for verification.
        new_password (str): New plain-text password to hash.
        user_id (str, optional): User ID for logging.

    Returns:
        str: New password hash.
    """
    is_valid = verifyPassword(old_password_plain, old_hash, user_id=user_id)
    if not is_valid:
        raise ValueError("Invalid Password")
    
    return hash_password(new_password, user_id=user_id)
