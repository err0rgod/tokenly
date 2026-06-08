"""
Middleware module providing authentication decorators for protecting API endpoints.
Integrates with jwtHandler and handleJwtBlacklist to verify access tokens.
"""

from functools import wraps
from session.jwt_handler import jwtHandler
from session.blacklist import handleJwtBlacklist
import logging

logger = logging.getLogger(__name__)

def require_auth(jwt_handler: jwtHandler, blacklist_manager: handleJwtBlacklist = None):
    """
    Decorator to enforce JWT authentication on a function.

    Verifies the provided JWT token using the jwt_handler and checks if the token 
    is blacklisted using the optional blacklist_manager.

    Args:
        jwt_handler (jwtHandler): Instance of jwtHandler to verify tokens.
        blacklist_manager (handleJwtBlacklist, optional): Manager to check for revoked tokens.

    Returns:
        Callable: The decorated function that requires authentication.

    Raises:
        ValueError: If the authentication token is missing or revoked.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(token: str, *args, **kwargs):
            """
            Wrapper function that performs the authentication check.

            Args:
                token (str): The JWT access token from the request.
                *args: Variable length argument list for the decorated function.
                **kwargs: Arbitrary keyword arguments for the decorated function.

            Returns:
                Any: The result of the decorated function if authentication succeeds.
            """
            logger.info("Initiated authentication check")
            if not token:
                logger.warning("Authentication token missing")
                raise ValueError("Authentication token is missing")
            
            # Verify and decode JWT
            payload = jwt_handler.verifyJwt(token)

            # Check database for blacklisted JTI
            if blacklist_manager and blacklist_manager.is_token_blacklisted(payload.get("jti")):
                logger.warning("Token was revoked.")
                raise ValueError("Token has been revoked")
            
            # Pass the decoded payload to the original function
            return func(payload, *args, **kwargs)
        return wrapper
    return decorator