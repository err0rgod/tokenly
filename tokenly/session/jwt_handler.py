"""
Module for handling JSON Web Token (JWT) generation and verification.
Provides functionality for creating access tokens and refresh session objects.
"""

import hashlib
import jwt
from tokenly.model.models import userdata, refreshSession
from datetime import datetime, timedelta, timezone
import uuid
import logging
import secrets

logger = logging.getLogger(__name__)

class jwtHandler:
    """
    Handles JWT operations including creation and verification.

    Attributes:
        SECRET_KEY (str): The secret key used for signing and verifying tokens.
        algorithm (str): The algorithm used for JWT encoding/decoding (default: "RS256").
    """

    def __init__(self, SECRET_KEY: str, algorithm: str | None = "HS256") -> None:
        """
        Initializes the jwtHandler with security credentials.

        Args:
            SECRET_KEY (str): Secret key for JWT.
            algorithm (str, optional): JWT signing algorithm. Defaults to "RS256".
        """
        self.SECRET_KEY = SECRET_KEY
        self.algorithm = algorithm

    def createJwt(self, User: userdata, jwt_mins: int | None = 15, refresh_days: int | None = 7, *args, **kwargs) -> tuple[str, str, refreshSession]:
        """
        Creates a new JWT access token and a corresponding refresh session.

        Args:
            User (userdata): The user for whom the tokens are being created.
            jwt_mins (int, optional): Access token expiration in minutes. Defaults to 15.
            refresh_days (int, optional): Refresh token expiration in days. Defaults to 7.

        Returns:
            tuple[str, str, refreshSession]: A tuple containing:
                - access_token (str): The encoded JWT access token.
                - raw_refresh_token (str): The plain-text refresh token for the client.
                - session_obj (refreshSession): The SQLModel object representing the refresh session.
        """
        # Using UTC for global consistency
        now = datetime.now(timezone.utc)
        
        # JWT Payload structure
        exp = timedelta(minutes=jwt_mins)
        jti = str(uuid.uuid4())
        data = {
            "sub": User.user_id,
            "jti": jti,
            "user_name": User.user_name,
            "iat": now,
            "exp": now + exp
        }
        
        # Encode Access Token
        access_token = jwt.encode(data, self.SECRET_KEY, algorithm=self.algorithm)
        
        # Generate Refresh Token
        raw_refresh_token = secrets.token_urlsafe(64)
        refresh_token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()

        # Create Refresh Session Object
        session_obj = refreshSession(
            session_id=str(uuid.uuid4()),
            user_id=User.user_id,
            token_hash=refresh_token_hash,
            expires_at=now + timedelta(days=refresh_days)
        )

        return access_token, raw_refresh_token, session_obj

    def verifyJwt(self, token: str) -> dict:
        """
        Verifies and decodes a JWT access token.

        Args:
            token (str): The encoded JWT token string.

        Returns:
            dict: The decoded token payload.

        Raises:
            ValueError: If the token has expired or is invalid.
        """
        try:
            decoded = jwt.decode(token, self.SECRET_KEY, algorithms=[self.algorithm])
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise ValueError("Token has Expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid Token")
            raise ValueError("Invalid Token")