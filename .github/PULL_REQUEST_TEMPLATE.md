## What this changes

<!-- One or two sentences. Link the issue if there is one: Closes #123 -->

## Why

<!-- The problem this solves. If it is an API change, say what breaks. -->

## How it was verified

<!-- Real commands and output, not "should work". -->
```
$ pytest -q
$ ruff check .
```

## Checklist

- [ ] Tests added or updated for the new behaviour
- [ ] `pytest -q` passes locally
- [ ] `ruff check .` is clean
- [ ] Docstrings have `Args` / `Returns` / `Raises` where relevant
- [ ] README/docs snippet updated if user-facing (it is executed by `tests/test_docs_examples.py`)
- [ ] `CHANGELOG.md` has an entry under `Unreleased`
- [ ] No new runtime dependency, no ORM, no framework import inside `tokenly_auth/`
- [ ] No secret or token written to a log

## Breaking change?

<!-- If yes: what is the migration path, and is there a deprecation shim? -->
