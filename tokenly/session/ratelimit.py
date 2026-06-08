"""
Module for implementing rate limiting.
Provides a storage-agnostic rate limiter that can be used to prevent 
brute-force attacks or API abuse.
"""

import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Implements a simple rate limiting mechanism using a storage client (e.g., Redis).

    Attributes:
        storage (Any): The storage client instance (must support `incr` and `expire`).
        maxRequests (int): Maximum number of allowed requests within the window.
        window (int): Time window in seconds for the rate limit.
    """

    def __init__(self, storage_client, max_requests: int = 10, window: int = 60):
        """
        Initializes the RateLimiter.

        Args:
            storage_client (Any): Client for storing rate limit counters (e.g., Redis).
            max_requests (int, optional): Max requests allowed. Defaults to 10.
            window (int, optional): Time window in seconds. Defaults to 60.
        """
        self.storage = storage_client
        self.maxRequests = max_requests
        self.window = window

    def check_limit(self, identifier: str, action: str = "login") -> int:
        """
        Checks if the rate limit has been exceeded for a specific identifier and action.

        Args:
            identifier (str): Unique identifier for the client (e.g., IP address or username).
            action (str, optional): The action being rate limited. Defaults to "login".

        Returns:
            int: The current request count for the identifier.

        Raises:
            ValueError: If the rate limit has been exceeded.
        """
        key = f"ratelimit:{action}:{identifier}"

        # Increment the counter in storage
        count = self.storage.incr(key)

        # Set expiration on the first request in a new window
        if count == 1:
            self.storage.expire(key, self.window)
            
        if count > self.maxRequests:
            logger.warning(f"Rate Limit exceeded by {identifier}.")
            raise ValueError(f"Rate limit exceeded. Try again in {self.window} seconds")
            
        return count