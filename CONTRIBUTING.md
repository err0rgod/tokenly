# Contributing to Tokenly Auth

Thanks for being here. This is a small, focused library, and the bar is simple: **security
primitives must be correct, and the API must stay boring.**

## Ways to help

- **Report a bug** — use the bug template. A failing snippet beats a paragraph.
- **Request a feature** — use the feature template and explain the use case, not the API shape.
- **Improve docs** — the docs site repo is [`tokenly-auth-docs`](https://github.com/err0rgod/tokenly-auth-docs); typo PRs are welcome and merged fast.
- **Pick up a `good first issue`** — these are scoped so you can finish one in an evening.
- **Review** — a second pair of eyes on token handling is always worth it.

## Development setup

```bash
git clone https://github.com/err0rgod/tokenly
cd tokenly
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
ruff check .
```

Python 3.9+ is required. No Docker, no services, no database — the test suite is pure CPU.

## Ground rules

1. **No new runtime dependencies** without an issue and sign-off. A security library with a fat
   dependency tree is a liability. `pyjwt`, `argon2-cffi`, and `revlimiter` are the budget.
2. **No framework imports in `tokenly_auth/`.** FastAPI, Flask, Django must never appear in
   library code — only in docs examples. That is the whole point of the library.
3. **No database code.** If a patch needs a connection object, it belongs in the caller's app.
4. **Tests come with the change.** A behaviour change without a test will be asked for one.
5. **Never write a secret to a log.** Reviewers will block on it.

## Pull request flow

1. Fork, or branch off `main` (`feat/…`, `fix/…`, `docs/…`).
2. Make the change **plus** tests. Keep the diff focused — one concern per PR.
3. Run `pytest -q` and `ruff check .` locally. CI runs both on 3.9–3.13, Linux and macOS.
4. Open the PR and fill in the template: what changed, why, and how you verified it.
5. A maintainer reviews. Expect questions about edge cases — that is the job.

Squash-merge is the default. PR titles follow [Conventional Commits](https://www.conventionalcommits.org/)
(`fix:`, `feat:`, `docs:`, `chore:`), because the changelog is generated from them.

## Adding a public API

The public surface is what `tokenly_auth/__init__.py` re-exports. Anything new needs:

- a docstring with `Args` / `Returns` / `Raises`
- a test in `tests/` (and, if user-facing, a README or docs snippet — README snippets are
  executed by `tests/test_docs_examples.py`, so keep them runnable)
- a note in `CHANGELOG.md` under `Unreleased`

**Breaking changes** to existing names require a deprecation period: keep the old name working
with a `DeprecationWarning` for one minor release first.

## Releasing (maintainers)

1. Bump `version` in `pyproject.toml` **and** `__version__` in `tokenly_auth/__init__.py`. They
   must match — CI does not check this yet, so check it yourself.
2. Move `CHANGELOG.md` entries from `Unreleased` into a dated section.
3. Commit, tag `vX.Y.Z`, push the tag, and publish a GitHub Release.
4. The `publish.yml` workflow builds and uploads to PyPI via **Trusted Publishing** (OIDC — no
   API token in the repo). One-time PyPI setup, as a maintainer:
   *pypi.org → project → Publishing → add publisher* — owner `err0rgod`, repo `tokenly`,
   workflow `publish.yml`, environment `pypi`.
5. Verify: `pip install --upgrade tokenly-auth` in a clean venv and check `tokenly_auth.__version__`.

## Code of conduct

Be decent. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
