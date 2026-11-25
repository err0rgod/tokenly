"""Tests for the credential-structure validator decorator."""

import pytest

from tokenly_auth import validate_creds_structure


@validate_creds_structure
def register(username: str, password: str):
    return "ok"


def test_accepts_valid_credentials():
    assert register("nirbhay", "SecurePass1!") == "ok"


@pytest.mark.parametrize(
    "username,password,message",
    [
        ("", "SecurePass1!", "Username and password are required"),
        ("nirbhay", "", "Username and password are required"),
        ("ab", "SecurePass1!", "Username must be between 3 and 15 characters"),
        ("a" * 16, "SecurePass1!", "Username must be between 3 and 15 characters"),
        ("nir_bhay", "SecurePass1!", "Username must be alphanumeric"),
        ("nirbhay", "Short1!", "Password must be at least 8 characters long"),
        ("nirbhay", "securepass1!", "Password must contain at least one uppercase letter"),
        ("nirbhay", "SECUREPASS1!", "Password must contain at least one lowercase letter"),
        ("nirbhay", "SecurePass!", "Password must contain at least one digit"),
        ("nirbhay", "SecurePass1", "Password must contain at least one special character"),
    ],
)
def test_rejects_invalid_credentials(username, password, message):
    with pytest.raises(ValueError, match=message):
        register(username, password)
