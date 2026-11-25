"""Tests for hash-upgrade detection (GitHub issue #7).

Covers:
- needs_password_rehash returns False for a current hash.
- needs_password_rehash returns True for a deliberately weak hash.
- verify_and_rehash on a weak hash with correct password returns (True, new_hash)
  and the new hash is itself current.
- verify_and_rehash on a current hash with correct password returns (True, None).
- verify_and_rehash with the wrong password returns (False, None).
- needs_password_rehash("not-a-hash") returns False and does not raise.
- Security["needs_rehash"] and Security["verify_and_rehash"] aliases are wired.
"""

import argon2

from tokenly_auth import Security
from tokenly_auth.crypto.passwords import (
    hash_password,
    needs_password_rehash,
    verify_and_rehash,
)

PASSWORD = "correct-horse-battery-staple"

# A PasswordHasher with deliberately weak parameters, used only to produce test fixtures.
_WEAK_PH = argon2.PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)


# ---------------------------------------------------------------------------
# needs_password_rehash
# ---------------------------------------------------------------------------


def test_current_hash_does_not_need_rehash():
    """A hash produced with the current default parameters should not need upgrading."""
    current_hash = hash_password(PASSWORD)
    assert needs_password_rehash(current_hash) is False


def test_weak_hash_needs_rehash():
    """A hash produced with weaker-than-default parameters must signal an upgrade."""
    weak_hash = _WEAK_PH.hash(PASSWORD)
    assert needs_password_rehash(weak_hash) is True


def test_malformed_hash_returns_false_without_raising():
    """An unparseable string must return False, not propagate an exception."""
    result = needs_password_rehash("not-a-hash")
    assert result is False


# ---------------------------------------------------------------------------
# verify_and_rehash
# ---------------------------------------------------------------------------


def test_verify_and_rehash_weak_correct_password():
    """Correct password + weak hash → (True, new_hash) where new_hash is current."""
    weak_hash = _WEAK_PH.hash(PASSWORD)
    ok, new_hash = verify_and_rehash(PASSWORD, weak_hash)

    assert ok is True
    assert new_hash is not None
    # The freshly-produced hash should itself be current.
    assert needs_password_rehash(new_hash) is False


def test_verify_and_rehash_current_correct_password():
    """Correct password + current hash → (True, None); no rehash needed."""
    current_hash = hash_password(PASSWORD)
    ok, new_hash = verify_and_rehash(PASSWORD, current_hash)

    assert ok is True
    assert new_hash is None


def test_verify_and_rehash_wrong_password():
    """Wrong password → (False, None) regardless of hash age."""
    current_hash = hash_password(PASSWORD)
    ok, new_hash = verify_and_rehash("wrong-password", current_hash)

    assert ok is False
    assert new_hash is None


# ---------------------------------------------------------------------------
# Security dict aliases
# ---------------------------------------------------------------------------


def test_security_needs_rehash_alias_is_callable():
    """Security['needs_rehash'] must point to needs_password_rehash and work."""
    fn = Security["needs_rehash"]
    assert callable(fn)
    current_hash = hash_password(PASSWORD)
    assert fn(current_hash) is False


def test_security_verify_and_rehash_alias_is_callable():
    """Security['verify_and_rehash'] must point to verify_and_rehash and work."""
    fn = Security["verify_and_rehash"]
    assert callable(fn)
    current_hash = hash_password(PASSWORD)
    ok, new_hash = fn(PASSWORD, current_hash)
    assert ok is True
    assert new_hash is None
