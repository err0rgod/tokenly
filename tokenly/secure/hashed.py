"""
Security module for password hashing and verification.
Uses Argon2 for secure password hashing and provides brute-force protection
by tracking failed attempts and locking accounts temporarily.
"""

from argon2 import PasswordHasher
from model.models import userdata, refreshSession
from validations.structure import validate_creds_structure 
from datetime import datetime, timedelta, timezone
import logging
from sqlmodel import Session, select

# Initializing the password hashing and logging objects
ph = PasswordHasher()
logger = logging.getLogger(__name__)

@validate_creds_structure
def hash_password(User: userdata) -> userdata:
    """
    Hashes the user's password using Argon2.

    Args:
        User (userdata): The user object containing the plain-text password.

    Returns:
        userdata: The user object with the password replaced by its hash.
    """
    logger.info(f"Password Hashed of {User.user_id}")
    hash = ph.hash(User.password)
    User.password = hash
    return User


def verifyPassword(User: userdata, hash: str) -> bool:
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
    if User.locked_until and now < User.locked_until:
        logger.warning(f"account locked of user {User.user_id}")
        raise ValueError("Account Locked Try again Later.")
    try:
        valid = ph.verify(User.password, hash)
        if valid:
            logger.info("Password verified successfully")
            User.failed_attempts = 0
            User.locked_until = None
            return True
    except Exception:
        logger.warning(f"Invalid hash by {User.user_id} brute-force protection initiated")
        User.failed_attempts += 1
        if User.failed_attempts >= 5:
            User.locked_until = now + timedelta(minutes=15)
        return False


def resetPassword(User: userdata, session: Session, new_password: str, old_password_plain: str) -> bool:
    """
    Resets the user's password after verifying the old password.
    Revokes all active refresh sessions for the user upon successful reset.

    Args:
        User (userdata): The user object whose password is to be reset.
        session (Session): The active database session.
        new_password (str): The new plain-text password.
        old_password_plain (str): The current plain-text password for verification.

    Returns:
        bool: True if the reset was successful, False if the user was not found.

    Raises:
        ValueError: If the old password verification fails.
    """
    is_valid = verifyPassword(User, old_password_plain)
    if not is_valid:
        raise ValueError("Invalid Credentials")
    else:
        hashed_new_password = ph.hash(new_password)
        statement = select(userdata).where(userdata.user_id == User.user_id)
        results = session.exec(statement).first()
        if results:
            results.password = hashed_new_password
            session.add(results)
            session.commit()
            
            # Revoke active refresh tokens
            token_statement = select(refreshSession).where(
                (refreshSession.user_id == User.user_id) & (refreshSession.revoked == False)
            )
            active_tokens = session.exec(token_statement).all()

            for token in active_tokens:
                token.revoked = True
                session.add(token)
            session.commit()

            logger.info(f"Password changed and {len(active_tokens)} tokens revoked for {User.user_id}")
            return True
        else:
            return False