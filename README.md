# Tokenly

Tokenly is a professional-grade Python library designed to handle Hybrid state authentication, session management, and security concerns for modern web applications. It provides a robust set of tools for password hashing, JWT management, rate limiting, and brute-force protection.

## Core Features

- **Secure Password Management:** Uses Argon2 hashing with built-in brute-force protection and account locking.
- **JWT Handling:** Full support for access token generation, verification, and blacklisting.
- **Session Persistence:** Secure refresh token rotation and validation logic.
- **Rate Limiting:** Storage-agnostic rate limiting to prevent API abuse.
- **Data Integrity:** SQLModel-based schemas for easy integration with relational databases.
- **Validation:** Strict structural validation for user credentials.

## Installation

Ensure you have the required dependencies installed:

```bash
pip install sqlmodel pyjwt argon2-cffi
```

## Quick Start

### 1. Database Setup

Tokenly uses SQLModel, allowing for easy database integration. You can use the provided `DatabaseManager` to initialize your database.

```python
from tokenly import DatabaseManager

db = DatabaseManager(db_url="sqlite:///./auth.db")

# Create tables (Run this during initial setup)
db.init_db()

# Get a session
with next(db.get_session()) as session:
    # Use the session with Tokenly functions
    pass
```

### 2. Password Hashing and Verification

```python
from tokenly import userdata, hash_password, verifyPassword

# Create a user object
user = userdata(
    user_id="user_01",
    user_name="john_doe",
    password="MySecurePassword123!"
)

# Hash the password before saving to DB
hash_password(user)

# Verify the password later
is_valid = verifyPassword(user, "MySecurePassword123!")
```

### 3. JWT Generation

```python
from tokenly import jwtHandler

handler = jwtHandler(SECRET_KEY="your_secret_key", algorithm="HS256")
access_token, raw_refresh, session_obj = handler.createJwt(user)
```

### 4. Protecting Routes

```python
from tokenly import require_auth

@require_auth(jwt_handler=handler)
def get_user_profile(payload):
    return f"Welcome {payload['user_name']}"
```

## Security Design

Tokenly is built with security-first principles:
- **Argon2id:** Utilizes the industry-standard password hashing algorithm.
- **Token Rotation:** Refresh tokens are single-use; a new one is generated upon every refresh.
- **Brute-Force Protection:** Automatically locks accounts for 15 minutes after 5 failed attempts.
- **Blacklisting:** Enables immediate revocation of tokens during logout or security breaches.

## Testing

The library includes a comprehensive suite of unit tests. To run the tests, use:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License.
