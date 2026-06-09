"""
Security module for password hashing and verification.
Uses Argon2 for secure password hashing and provides brute-force protection
by tracking failed attempts and locking accounts temporarily.
"""

from argon2 import PasswordHasher
from tokenly_auth.validators.credentials import validate_creds_structure
from datetime import datetime, timedelta, timezone
import logging
# from sqlmodel import Session, select

# Initializing the password hashing and logging objects
ph = PasswordHasher()
logger = logging.getLogger(__name__)


def hash_password(password: str, user_id: str | None = None) -> str:
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


def verifyPassword(password: str, hash: str, user_id : str | None = None,locked_until : datetime | None = None) -> bool:
    """
    Verifies a plain-text password against a stored hash and implements brute-force protection.

    If the account is locked, it raises a ValueError. On failure, it increments
    the failed_attempts counter and locks the account if it exceeds the limit.

    Args:
        User (userdata): The user object from the database.
        hash (str): The plain-text password to verify.

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
        valid = ph.verify(password, hash)
        if valid:
            logger.info("Password verified successfully")
            failed_attempts = 0
            locked_until = None
            return True
    except Exception:
        logger.warning(f"Invalid hash by {user_id} brute-force protection initiated")
        failed_attempts += 1
        if failed_attempts >= 5:
            locked_until = now + timedelta(minutes=15)
        return False


def resetPassword(old_hash: str, old_password_plain: str, new_password: str, user_id: str | None = None) -> str:
    """
    Utility to verify old password and generate a new hash.
    Does not touch the database.

    Args:
        old_hash (str): Current stored password hash.
        old_password_plain (str): Current plain-text password for verification.
        new_password (str): New plain-text password to hash.
        user_id (str, optional): User ID for logging.

    Returns:
        str: New password hash.
    """
    # NOTE: verifyPassword expects parameters in specific order
    is_valid = verifyPassword(old_password_plain, old_hash)
    if not is_valid:
        raise ValueError("Invalid Password")
    else:
        hashed_new_password = ph.hash(new_password)
        return hashed_new_password
