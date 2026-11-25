# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Wheel smoke test in CI (installs the built wheel into a clean venv and imports it).
- `pytest-cov`, `ruff`, and local `build`/`twine` in a `dev` extra; coverage config with branch coverage.
- Executable README examples (`tests/test_docs_examples.py`) so documented snippets cannot rot.
- Test suites for the rate limiter, the credential validator, and the `require_auth` decorator.
- `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, issue forms, and a PR template.

### Changed
- CI matrix now covers Python 3.9–3.13 on Linux plus 3.12 on macOS, with pip caching, ruff, and coverage.
- Publishing moved to PyPI **Trusted Publishing** (OIDC) with a build/`twine check` stage and an
  artifact hand-off, replacing the token-based single-job upload. Releases now trigger on
  `published` rather than `created`, so drafts no longer publish early.
- README rewritten: honest positioning ("toolkit, not framework"), a comparison table, a
  security-model section, and a roadmap.
- `requires-python` raised to `>=3.9` (3.8 is end-of-life and was untested).
- Package metadata: more classifiers, keywords, and project URLs (docs, changelog, source).

### Fixed
- Tracked build artifacts (`dist/`, `tokenly_auth.egg-info/`) removed from the repository;
  `.gitignore` already covered them.
- Unused imports flagged by ruff in `crypto/passwords.py`, `tokens/refresh.py`, and `tests/test_security.py`.

## [1.1.4] — unreleased at tag time

### Added
- Password hash upgrade detection groundwork (`needs_password_rehash` / rehash-on-verify path).

### Fixed
- Session helpers return the raw refresh token instead of a pre-hashed value, matching the
  documented rotation flow (verify-then-hash-on-store).

## [1.1.3] — 2026-07-22
- Documentation and metadata fixes. **PyPI publish failed for this tag**, so it never shipped.

## [1.1.2] — 2026-07-22
- Restored the `tokenly-auth` distribution name after the `fastapi-auth` experiment.

## [1.1.1] — 2026-07-22
- Version bump accompanying the rename.

## [1.1.0] — 2026-07-22
- Renamed the distribution to `fastapi-auth` (reverted in 1.1.2).

## [1.0.0] — 2026-06-09
- Initial stable release: Argon2 password hashing, JWT creation/verification, refresh-token
  hashing, storage-agnostic rate limiting, `require_auth`, credential validation.

## [0.1.0] — 2026-06-08
- First public preview.
