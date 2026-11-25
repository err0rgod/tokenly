"""Tests for the storage-agnostic rate limiter."""

import pytest

from tokenly_auth import RateLimiter


class FakeStore:
    """Redis-like shim implementing just incr/expire."""

    def __init__(self):
        self.counters = {}
        self.expirations = {}
        self.calls = []

    def incr(self, key):
        self.calls.append(("incr", key))
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key, seconds):
        self.calls.append(("expire", key, seconds))
        self.expirations[key] = seconds
        return True


def test_allows_requests_under_the_limit():
    store = FakeStore()
    limiter = RateLimiter(store, max_requests=3, window=30)

    assert limiter.check_limit("1.2.3.4") == 1
    assert limiter.check_limit("1.2.3.4") == 2
    assert limiter.check_limit("1.2.3.4") == 3


def test_blocks_past_the_limit():
    limiter = RateLimiter(FakeStore(), max_requests=2, window=30)
    limiter.check_limit("1.2.3.4")
    limiter.check_limit("1.2.3.4")

    with pytest.raises(ValueError, match="Rate limit exceeded"):
        limiter.check_limit("1.2.3.4")


def test_sets_ttl_only_on_first_request():
    store = FakeStore()
    limiter = RateLimiter(store, max_requests=10, window=45)
    limiter.check_limit("1.2.3.4")
    limiter.check_limit("1.2.3.4")

    expiries = [c for c in store.calls if c[0] == "expire"]
    assert len(expiries) == 1
    assert expiries[0] == ("expire", "ratelimit:login:1.2.3.4", 45)


def test_identifiers_and_actions_are_isolated():
    store = FakeStore()
    limiter = RateLimiter(store, max_requests=1, window=60)

    limiter.check_limit("alice", action="login")
    limiter.check_limit("bob", action="login")
    limiter.check_limit("alice", action="signup")

    assert set(store.counters) == {
        "ratelimit:login:alice",
        "ratelimit:login:bob",
        "ratelimit:signup:alice",
    }
