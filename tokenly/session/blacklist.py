"""
Module for managing JWT blacklisting.
Handles revoking tokens by storing their JTI (JWT ID) in the database.
"""

from sqlmodel import Session, select
from model.models import jwt_blacklist
from datetime import datetime

class handleJwtBlacklist:
    """
    Manages the blacklisting of JWT tokens to handle logouts and security revocations.

    Attributes:
        session (Session): The active database session used for queries.
    """

    def __init__(self, session: Session) -> None:
        """
        Initializes the blacklist manager with a database session.

        Args:
            session (Session): SQLModel database session.
        """
        self.session = session

    def debarJwt(self, jti: str, user_name: str, expired_at: datetime) -> None:
        """
        Adds a JWT identifier to the blacklist.

        Args:
            jti (str): The unique JWT identifier to blacklist.
            user_name (str): The username associated with the token.
            expired_at (datetime): The original expiration time of the token.
        """
        blacklist = jwt_blacklist(
            jti=jti,
            user_name=user_name,
            expired_at=expired_at
        )

        self.session.add(blacklist)
        self.session.commit()

    def is_token_blacklisted(self, jti: str) -> bool:
        """
        Checks if a given JWT identifier is in the blacklist.

        Args:
            jti (str): The JWT identifier to check.

        Returns:
            bool: True if the token is blacklisted, False otherwise.
        """
        statement = select(jwt_blacklist).where(jwt_blacklist.jti == jti)
        result = self.session.exec(statement).first()
        return result is not None