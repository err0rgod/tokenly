# Security Policy

Tokenly Auth handles password hashing, token signing, and refresh-token storage primitives.
Security reports are taken seriously and handled privately.

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.1.x   | ✅ |
| 1.0.x   | ⚠️ upgrade recommended — the published 1.0.0 build returns a *pre-hashed* refresh token, which differs from the documented flow |
| < 1.0   | ❌ |

## Reporting a vulnerability

**Do not open a public issue.**

- Use GitHub's private reporting: *Security → Report a vulnerability* on this repository.
- Or email the maintainer: nirbhayerror [at] gmail.com.

Please include:

- affected version (`tokenly_auth.__version__`)
- a minimal reproduction or proof-of-concept
- impact assessment — what an attacker gains
- any suggested fix

**What to expect:** acknowledgement within 72 hours, an assessment within 7 days, and a fix plus
coordinated advisory for confirmed issues. Credit is given in the advisory unless you ask
otherwise.

## Scope

In scope:

- Argon2id hashing and verification logic (`tokenly_auth.crypto.passwords`)
- JWT creation/verification, algorithm confusion, `alg: none` handling (`tokenly_auth.tokens.jwt`)
- refresh-token hashing and rotation helpers (`tokenly_auth.tokens.refresh`)
- rate-limiter bypass or counter reset (`tokenly_auth.middleware.ratelimit`)
- authentication decorator bypass (`tokenly_auth.middleware.auth`)
- credential-validation bypass (`tokenly_auth.validators.credentials`)

Out of scope:

- Anything requiring the caller to leak their own `SECRET_KEY`
- Weak passwords the caller chose to allow (that is a policy decision in *your* app)
- Reports produced solely by a scanner without a working proof-of-concept

## Hardening notes for users

- Use a `SECRET_KEY` of at least 32 random bytes. HS256 with a short key is rejected by `pyjwt`
  with a warning for good reason.
- Store only the hash of a refresh token. `SessionManager.hash_refresh_token()` exists for that.
- Rotate refresh tokens on every use and revoke the `jti` on logout.
- Rate-limit the login endpoint, not just the API — `RateLimiter` takes any store with
  `incr`/`expire`.
