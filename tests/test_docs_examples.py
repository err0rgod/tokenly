"""Executable copies of the README snippets.

If a documented example ever stops working, this file fails. Keep it in sync with
README.md — it is the contract that the docs cannot silently lie.
"""

from tokenly_auth import (
    RateLimiter,
    Security,
    SessionManager,
    TokenHandler,
    require_auth,
    validate_creds_structure,
)

SECRET = "a-long-random-secret-at-least-32-bytes"


class DictStorage:
    """Minimal stand-in for Redis: implements the incr/expire protocol."""

    def __init__(self):
        self.data = {}

    def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    def expire(self, key, seconds):
        self.data[key + ":ttl"] = seconds
        return True


def test_readme_password_hashing():
    hashed = Security["hash"]("my_secure_password")
    assert hashed.startswith("$argon2")
    assert Security["verify"]("my_secure_password", hashed) is True
    assert Security["verify"]("wrong_password", hashed) is False

    new_hash = Security["reset"](hashed, "my_secure_password", "a_better_password")
    assert Security["verify"]("a_better_password", new_hash) is True


def test_readme_tokens():
    handler = TokenHandler(SECRET_KEY=SECRET)
    tokens = handler.createJwt(sub="user_id_123")

    assert set(tokens) == {"access_token", "refresh_token", "refresh_days"}

    payload = handler.verifyJwt(tokens["access_token"])
    assert payload["sub"] == "user_id_123"
    assert "jti" in payload

    session = SessionManager()
    stored = session.hash_refresh_token(tokens["refresh_token"])
    assert len(stored) == 64
    assert stored == session.hash_refresh_token(tokens["refresh_token"])


def test_readme_rate_limiter():
    limiter = RateLimiter(storage_client=DictStorage(), max_requests=5, window=60)

    for _ in range(5):
        limiter.check_limit(identifier="203.0.113.7", action="login")

    try:
        limiter.check_limit(identifier="203.0.113.7", action="login")
    except ValueError as exc:
        assert "Rate limit exceeded" in str(exc)
    else:  # pragma: no cover - guard against a silently disabled limiter
        raise AssertionError("rate limiter did not reject the 6th request")


def test_readme_require_auth():
    handler = TokenHandler(SECRET_KEY=SECRET)
    token = handler.createJwt(sub="user_id_123")["access_token"]

    @require_auth(jwt_handler=handler)
    def protected_route(payload):
        return f"Hello {payload['sub']}"

    assert protected_route(token) == "Hello user_id_123"


def test_readme_credential_validation():
    calls = []

    @validate_creds_structure
    def signup(username: str, password: str):
        calls.append((username, password))
        return True

    assert signup("nirbhay", "SecurePass1!") is True
    assert calls == [("nirbhay", "SecurePass1!")]
