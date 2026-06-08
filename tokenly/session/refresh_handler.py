"""
Module for managing refresh token rotation and validation.
Ensures secure session persistence by validating refresh tokens and 
enforcing rotation policies.
"""

from datetime import datetime, timezone
from tokenly.model.models import refreshSession, userdata
from sqlmodel import select, Session
import hashlib

class RefreshManager:
    """
    Manages the lifecycle of refresh tokens, including validation and rotation.

    Attributes:
        session (Session): The active database session.
    """

    def __init__(self, db_session: Session) -> None:
        """
        Initializes the RefreshManager with a database session.

        Args:
            db_session (Session): SQLModel database session.
        """
        self.session = db_session

    def validate_and_rotate(self, raw_refresh_token: str) -> str:
        """
        Validates a raw refresh token and marks it as revoked (rotated).

        Checks if the token exists, is not already revoked, and has not expired.
        If valid, it returns the user_id associated with the session.

        Args:
            raw_refresh_token (str): The plain-text refresh token from the client.

        Returns:
            str: The user_id associated with the refresh token.

        Raises:
            ValueError: If the token is invalid, revoked, or expired.
        """
        now = datetime.now(timezone.utc)

        # Hash the incoming raw token to match against the stored hash
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()

        # Query for the session object
        statement = select(refreshSession).where(refreshSession.token_hash == token_hash)
        db_token = self.session.exec(statement).first()

        if not db_token:
            raise ValueError("Invalid refresh token.")
        
        if db_token.revoked:
            # Security measure: If a revoked token is reused, it might indicate theft
            raise ValueError("Refresh token has been revoked. Possible theft detected.")
        
        if now > db_token.expires_at:
            raise ValueError("The refresh token has expired.")

        # Revoke the token (part of rotation: one-time use)
        db_token.revoked = True
        self.session.add(db_token)
        self.session.commit()
        
        return db_token.user_id