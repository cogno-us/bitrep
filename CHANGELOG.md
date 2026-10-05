## Unreleased — proposed verification contract v1

- Enforce versioned Ed25519 verification before admission, with signed content commitments and operator-managed issuer trust.
- Isolate new accepted evidence from legacy data; enforce issuer/ID uniqueness and current-time duplicate re-verification.
- Define expiry, rotation, conservative revocation and historical limitations.
- Disable demonstration/placeholder assurance; add adversarial HTTP/storage tests and executable synthetic vector.
- Breaking input/read migration; see `docs/VERIFICATION_CONTRACT_V1.md` (pending Governor review).

# Changelog

All notable changes to BitRep will be documented in this file.

## [0.4.0] - 2026-03-08
### Changed
- Removed deprecated reputation scoring system; migrated to canonical binary-attestation model.
- Attestation model now reflects `{issuer, subject, attestation_type, signature, timestamp, anchor}`.
- Removed `weight`, `value`, `from_user`, `to_user`, `context`, and `mutual_validation` fields from attestations.
- Removed `reputation_score` from user identity model.
- Replaced PageRank-based weighted reputation with direct binary attestation queries.
- Replaced quadratic reputation-weighted governance voting with one-identity-one-vote.
- Updated ZK proof to prove attestation-count threshold (not reputation score).
- Removed reputation band privacy endpoint.

### Removed
- `utils/reputation.py` — weighted PageRank scoring engine deleted.
- `tests/test_reputation.py` — scoring unit tests deleted.

## [0.3.0] - Initial Public Release
### Added
- identity module with RSA keypair generation
- attestation issuance and validation
- reputation scoring using modified PageRank
- governance module with quadratic voting
- FastAPI service with modular routers
- full test suite (28/28 passing)
- architecture, security, and protocol documentation

### Changed
- improved input validation across endpoints
- normalized attestation weights for Sybil resistance

### Fixed
- signature verification edge cases
- timestamp skew handling

## [0.2.0] - Pre‑Release
- added attestation storage
- added basic reputation computation
- added initial API endpoints

## [0.1.0] - Prototype
- initial project structure
- identity generation
