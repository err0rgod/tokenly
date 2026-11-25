"""
Module for managing refresh token rotation and validation.
Ensures secure session persistence by validating refresh tokens and
enforcing rotation policies.
"""

import hashlib


class RefreshManager:
    """
    Utility for managing refresh token security operations.
    """
        
    def hash_refresh_token(self, raw_refresh_token: str) -> str:
        """
        Hashes a raw refresh token for secure database storage and comparison.

        Args:
            raw_refresh_token (str): The plain-text refresh token from the client.

        Returns:
            str: The SHA256 hash of the refresh token.
        """

        # Hash the incoming raw token to match against the stored hash
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()

        return token_hash
