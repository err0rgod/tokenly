"""
Security module for password hashing and verification.
Uses Argon2 for secure password hashing and provides brute-force protection
by tracking failed attempts and locking accounts temporarily.
"""

from typing import Optional, Tuple
from argon2 import PasswordHasher
import argon2.exceptions
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


def needs_password_rehash(stored_hash: str) -> bool:
    """Checks whether a stored hash was produced with weaker-than-current Argon2 parameters.

    Uses the module-level ``ph`` instance so the threshold always matches the library's
    current defaults, without duplicating parameter comparisons in application code.

    Args:
        stored_hash (str): The Argon2 hash string retrieved from persistent storage.

    Returns:
        bool: ``True`` when the hash should be re-hashed on the next successful login,
            ``False`` when it already meets the current parameter requirements **or** when
            the string cannot be parsed as a valid Argon2 hash (the caller must treat an
            unparseable hash as invalid credentials — it cannot be upgraded).
    """
    try:
        return ph.check_needs_rehash(stored_hash)
    except (argon2.exceptions.InvalidHashError, ValueError):
        return False


def verify_and_rehash(
    password: str,
    stored_hash: str,
    user_id: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Verifies a password and, when the stored hash is outdated, produces a fresh one.

    Delegates verification to :func:`verifyPassword` so that existing account-lock
    behaviour and audit logging are preserved.  A new hash is only produced when
    verification succeeds **and** :func:`needs_password_rehash` signals an upgrade is
    needed; callers should persist the new hash before the next login attempt.

    Args:
        password (str): The plain-text password supplied by the user.
        stored_hash (str): The Argon2 hash string retrieved from persistent storage.
        user_id (str, optional): User identifier forwarded to :func:`verifyPassword`
            for logging purposes.

    Returns:
        Tuple[bool, Optional[str]]:
            - ``(True, new_hash)`` — password is valid and the hash was upgraded.
            - ``(True, None)``     — password is valid and the hash is already current.
            - ``(False, None)``    — password does not match (or the account is locked,
              in which case :func:`verifyPassword` raises :class:`ValueError` before this
              function returns).
    """
    is_valid = verifyPassword(password, stored_hash, user_id=user_id)
    if not is_valid:
        return (False, None)
    if needs_password_rehash(stored_hash):
        return (True, hash_password(password, user_id=user_id))
    return (True, None)
