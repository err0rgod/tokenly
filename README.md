# Tokenly Auth

**Database-agnostic authentication primitives for Python — Argon2id hashing, JWTs, refresh-token rotation, and rate limiting, with zero ORM opinions.**

[![Tests](https://github.com/err0rgod/tokenly/actions/workflows/tests.yml/badge.svg)](https://github.com/err0rgod/tokenly/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/tokenly-auth.svg)](https://pypi.org/project/tokenly-auth/)
[![Python versions](https://img.shields.io/pypi/pyversions/tokenly-auth.svg)](https://pypi.org/project/tokenly-auth/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-live-brightgreen.svg)](https://err0rgod.github.io/tokenly-auth-docs/)

---

## Why another auth library?

Most Python auth libraries want to own your database. They ship an ORM model, a migration, a
`User` table, and an opinion about your schema. If your users already live somewhere else — a
legacy Postgres, MongoDB, Redis, a multi-tenant setup, or an internal service — you end up
fighting the library instead of using it.

Tokenly takes the opposite approach: **it does the cryptography and gives you the result.** You
own the schema. You own the query. You decide where the hash is stored.

| | Tokenly Auth | Framework-coupled solutions |
|---|---|---|
| Database / ORM | **none — you choose** | SQLAlchemy, SQLModel, Django ORM |
| Framework | any (FastAPI, Flask, Django, Starlette, Litestar, bare WSGI) | usually one |
| What you get | hashing, JWTs, refresh rotation, rate limiting, validation | the above **plus** models and endpoints |
| Upgrade path | adopt it one primitive at a time | all-or-nothing |

It is a **toolkit, not a framework.** If you want a batteries-included `User` model with signup
endpoints, use `fastapi-users` or `django-allauth`. If you already have users stored somewhere
and need the security primitives to be correct, this is for you.

---

## Installation

```bash
pip install tokenly-auth
```

Requires Python 3.9+. Dependencies: `pyjwt`, `argon2-cffi`, `revlimiter`.

---

## Quick start

### 1. Password hashing (Argon2id)

```python
from tokenly_auth import Security

hashed = Security["hash"]("my_secure_password")
is_valid = Security["verify"]("my_secure_password", hashed)   # True
is_valid = Security["verify"]("wrong_password", hashed)       # False

# Change password: verify the old one, hash the new one
new_hash = Security["reset"](hashed, "my_secure_password", "a_better_password")
```

Hashes are Argon2id (`$argon2id$...`) with library-default parameters. Store the returned string
in whatever column you like — it is self-describing, so future parameter upgrades never
invalidate existing hashes.

### 2. Access + refresh tokens

```python
from tokenly_auth import TokenHandler, SessionManager

handler = TokenHandler(SECRET_KEY="a-long-random-secret-at-least-32-bytes")

tokens = handler.createJwt(sub="user_id_123")
# {
#   "access_token":  "<signed JWT>",
#   "refresh_token": "<raw, high-entropy token>",
#   "refresh_days":  7,
# }

payload = handler.verifyJwt(tokens["access_token"])
payload["sub"]   # "user_id_123"
payload["jti"]   # unique token id — store this if you need revocation
```

The refresh token comes back **raw** and must be hashed before storage:

```python
session = SessionManager()
stored = session.hash_refresh_token(tokens["refresh_token"])   # sha256 hex, safe to persist
```

> Rotate on every use: verify the submitted raw token against the stored hash, then issue a new
> pair and overwrite the stored hash. Never store the raw refresh token.

### 3. Rate limiting (bring your own store)

```python
from tokenly_auth import RateLimiter

limiter = RateLimiter(storage_client=redis_client, max_requests=5, window=60)

try:
    limiter.check_limit(identifier=client_ip, action="login")
except ValueError:
    ...  # 429 — try again in `window` seconds
```

Any object with `incr(key)` and `expire(key, seconds)` works: Redis, Valkey, a DynamoDB wrapper,
or a dict shim in tests.

### 4. Protecting a route

```python
from tokenly_auth import require_auth, TokenHandler

handler = TokenHandler(SECRET_KEY="a-long-random-secret-at-least-32-bytes")

@require_auth(jwt_handler=handler)
def protected_route(payload):
    return f"Hello {payload['sub']}"
```

`require_auth` is deliberately framework-neutral: it takes the raw bearer token as the first
argument and hands the decoded payload to your function. Wiring it into FastAPI or Flask is a
three-line adapter (see the docs).

### 5. Credential validation

```python
from tokenly_auth import validate_creds_structure

@validate_creds_structure
def signup(username: str, password: str):
    ...   # only reached if both pass the policy
```

Default policy: username 3–15 alphanumeric characters; password ≥ 8 chars with upper, lower,
digit, and symbol. Raises `ValueError` with a specific message per violation.

---

## Security model — what this library does *not* do

Being explicit is part of being trustworthy:

- It does **not** store anything. No database, no cache, no files.
- It does **not** manage sessions. Refresh rotation is a helper; the state machine is yours.
- It does **not** call your mailer, SMS gateway, or OAuth provider.
- It does **not** decide revocation. `jti` is exposed so *you* can blacklist it in Redis or SQL.

Every primitive is small and covered by tests. If you find a gap, see [SECURITY.md](SECURITY.md).

---

## Status & roadmap

Actively developed. The current release line is `1.x`; the API below is stable within it.

Planned for the next minor releases (tracked as issues):

- typed exception hierarchy (`InvalidTokenError`, `ExpiredTokenError`, `RateLimitExceeded`) instead of bare `ValueError`
- JWT claims support (`iss`, `aud`, `nbf`, `scope`, custom claims) and a callback-based revocation hook
- refresh-token rotation objects carrying `expires_at` / `jti` / `family_id`
- `RateLimitResult` with `remaining` / `reset_after` for `X-RateLimit-*` headers
- hash-upgrade detection (`needs_rehash`, `verify_and_rehash`)
- `Storage` protocols so the rate limiter is typed

---

## Development

```bash
git clone https://github.com/err0rgod/tokenly
cd tokenly
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the PR flow, [CHANGELOG.md](CHANGELOG.md) for release
history, and the [documentation site](https://err0rgod.github.io/tokenly-auth-docs/) for guides.

## License

MIT © Nirbhay Katiyar ([@err0rgod](https://github.com/err0rgod))
