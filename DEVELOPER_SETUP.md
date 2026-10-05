# Developer setup

Use Python 3.10+ and the repository root (the entrypoint is `main:app`).

```sh
git clone https://github.com/cogno-us/bitrep.git
cd bitrep
python -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/uvicorn main:app --reload
```

The tests provision isolated synthetic trust and databases. Do not deploy test keys.
For non-test acceptance, configure `BITREP_TRUST_REGISTRY` with a vetted operator-owned
snapshot. Without it, verification and accepted-record endpoints fail closed (503).
See [the proposed v1 contract](docs/VERIFICATION_CONTRACT_V1.md) for exact formats,
trust assumptions, migration and limitations. Dependencies remain unpinned; record
your tested environment and apply your deployment dependency policy.

The API's startup creates missing ORM tables. Existing legacy rows are not migrated
into accepted evidence. `db/schema.sql` also describes the additive v1 table.

`utils/crypto.py` retains legacy RSA helpers; v1 uses `utils/verification.py` and Ed25519.
No production cryptographic review, CodeQL run or deployment is implied by local tests.
