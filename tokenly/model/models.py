"""
Module for defining data models used throughout the Tokenly library.
This module uses SQLModel (built on SQLAlchemy and Pydantic) to define
database schemas for user data, token blacklisting, and session management.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class userdata(SQLModel, table=True):
    """
    Represents the primary user account information.

    Attributes:
        user_id (str): Unique identifier for the user (Primary Key).
        user_name (str): Unique username for authentication.
        password (str): Hashed password string.
        failed_attempts (int): Counter for tracking failed login attempts for brute-force protection.
        locked_until (Optional[datetime]): Timestamp until which the account is locked after multiple failures.
        sessions (List["refreshSession"]): Relationship to the user's refresh sessions.
    """
    user_id: str = Field(primary_key=True, nullable=False, unique=True, index=True)
    user_name: str = Field(unique=True, nullable=False, index=True)
    password: str = Field(nullable=False)
    failed_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)

    # Relationship to sessions
    sessions: List["refreshSession"] = Relationship(back_populates="user")


class jwt_blacklist(SQLModel, table=True):
    """
    Maintains a list of revoked or logged-out JWT identifiers (JTIs).

    Attributes:
        user_name (str): Username associated with the revoked token.
        jti (str): Unique JWT Identifier (Primary Key).
        expired_at (datetime): Timestamp when the token would have naturally expired.
    """
    user_name: str = Field(nullable=False, index=True)
    jti: str = Field(primary_key=True, nullable=False, index=True)
    expired_at: datetime = Field(nullable=False, index=True)


class refreshSession(SQLModel, table=True):
    """
    Stores refresh token sessions to enable long-lived authentication and token rotation.

    Attributes:
        session_id (str): Unique identifier for the session (Primary Key).
        user_id (str): Reference to the user who owns this session.
        token_hash (str): Hashed version of the refresh token for secure storage.
        expires_at (datetime): Expiration timestamp for the refresh token.
        revoked (bool): Flag indicating if the session has been manually revoked or rotated.
        user (userdata): The user object associated with this session.
    """
    session_id: str = Field(primary_key=True, nullable=False, index=True)
    user_id: str = Field(nullable=False, foreign_key="userdata.user_id", index=True)
    token_hash: str = Field(nullable=False, index=True)
    expires_at: datetime = Field(nullable=False, index=True)
    revoked: bool = Field(nullable=False, default=False, index=True)

    # Relationship back to user
    user: userdata = Relationship(back_populates="sessions")