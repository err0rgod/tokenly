"""Tests for the require_auth decorator."""

import pytest

from tokenly_auth import TokenHandler, require_auth

SECRET = "unit-test-secret-key-long-enough-for-hs256"


@pytest.fixture()
def handler():
    return TokenHandler(SECRET_KEY=SECRET)


@pytest.fixture()
def token(handler):
    return handler.createJwt(sub="user-42")["access_token"]


def test_passes_payload_to_wrapped_function(handler, token):
    @require_auth(jwt_handler=handler)
    def route(payload, suffix=""):
        return payload["sub"] + suffix

    assert route(token, suffix="!") == "user-42!"


def test_rejects_missing_token(handler):
    @require_auth(jwt_handler=handler)
    def route(payload):  # pragma: no cover - never reached
        return payload

    with pytest.raises(ValueError, match="Authentication token is missing"):
        route("")


def test_rejects_invalid_token(handler):
    @require_auth(jwt_handler=handler)
    def route(payload):  # pragma: no cover - never reached
        return payload

    with pytest.raises(ValueError, match="Invalid Token"):
        route("not.a.jwt")


def test_rejects_token_signed_with_another_key(token):
    other = TokenHandler(SECRET_KEY="a-completely-different-secret-key-value")

    @require_auth(jwt_handler=other)
    def route(payload):  # pragma: no cover - never reached
        return payload

    with pytest.raises(ValueError, match="Invalid Token"):
        route(token)


def test_rejects_revoked_token(handler, token):
    @require_auth(jwt_handler=handler, isBlacklisted=True)
    def route(payload):  # pragma: no cover - never reached
        return payload

    with pytest.raises(ValueError, match="Token has been revoked"):
        route(token)


def test_preserves_function_metadata(handler):
    @require_auth(jwt_handler=handler)
    def my_route(payload):
        """Docstring survives."""
        return payload

    assert my_route.__name__ == "my_route"
    assert my_route.__doc__ == "Docstring survives."
