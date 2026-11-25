from tokenly_auth.crypto.passwords import (
    hash_password,
    verifyPassword,
    resetPassword,
    needs_password_rehash,
    verify_and_rehash,
)
from tokenly_auth.tokens.jwt import jwtHandler
from tokenly_auth.tokens.refresh import RefreshManager
from tokenly_auth.middleware.auth import require_auth
from tokenly_auth.middleware.ratelimit import RateLimiter
from tokenly_auth.validators.credentials import validate_creds_structure

# Clean API Aliases
Security = {
    "hash": hash_password,
    "verify": verifyPassword,
    "reset": resetPassword,
    "needs_rehash": needs_password_rehash,
    "verify_and_rehash": verify_and_rehash,
}

# Standardized Naming Aliases
TokenHandler = jwtHandler
SessionManager = RefreshManager

__version__ = "1.1.4"
__all__ = [
    "hash_password",
    "verifyPassword",
    "resetPassword",
    "needs_password_rehash",
    "verify_and_rehash",
    "jwtHandler",
    "RefreshManager",
    "RateLimiter",
    "require_auth",
    "validate_creds_structure",
    "Security",
    "TokenHandler",
    "SessionManager",
]
