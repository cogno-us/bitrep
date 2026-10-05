# Verification workstream validation

Baseline: `572c00d5a6e73e74b383240a7f58c31c041b4174` in `cogno-us/bitrep`.

Commands executed from repository root:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
git diff --check
```

Baseline suite: 22 passed (the old tests permitted unsigned admissions and demonstration verification).
Final suite: 81 passed, 20 deprecation warnings. Warnings concern Starlette's HTTPX TestClient and legacy `datetime.utcnow()` calls. `pip check`: no broken requirements. `git diff --check`: clean.

Test environment: Python 3.12.14, FastAPI 0.142.2, SQLAlchemy 2.1.3, Pydantic 2.13.5, cryptography 50.0.2, pytest 9.1.1, HTTPX 0.28.1, Starlette 1.7.0. Dependencies are not pinned by this repository; this records the tested environment, not a universal compatibility guarantee.

Coverage includes real Ed25519 signing; valid admission and read-only verification; modifications to signed fields; invalid signatures; wrong signer/issuer substitution; unknown key; missing/extra/malformed fields; duplicate JSON members; input size; unsupported protocol/algorithm; audience mismatch; current key/attestation time boundaries; revoked and rotated keys; idempotent retry; issuer/ID conflict; expired/revoked replay; operator trust-file reload/failure/freshness; database uniqueness; four concurrent submissions with independent SQLite sessions yielding one acceptance plus three duplicates; legacy row isolation; disabled privacy/identity/platform assurance; exact canonical consumer vector.

Rejected submissions are checked against accepted storage counts. The test database dependencies are now isolated per test; baseline fixtures created a test database but did not override API database dependencies.

Unsupported/unvalidated: real ZK or selective disclosure, historical as-of verification, external proposition truth, external content availability, institutional authorization, signed portable receipts, production trust enrollment/distribution/rollback prevention, non-SQLite concurrency, production migrations/deployment/load, independent cryptographic review and remote CI. No other repository's integration has been run.
