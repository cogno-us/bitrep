> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# BitRep Integrations

BitRep supports importing attestations from external platforms to enrich the trust graph. This document describes available integrations and planned extensions.

## Supported Integrations

### GitHub
- verify commit history
- validate repository contributions
- optional: signed commit verification

### LinkedIn
- import endorsements
- import work history metadata
- optional: role verification via employer signature

### StackOverflow
- import reputation score
- import badge metadata
- optional: tag‑specific expertise weighting

### eBay
- import seller ratings
- import transaction feedback
- optional: dispute‑resolution metadata

---

## Planned Integrations
- Mastodon (WebFinger identity binding)
- Twitter/X (verified account binding)
- Discord (server‑level attestations)
- Reddit (karma‑based weighting)
- academic identity providers (ORCID)

---

## Integration Principles
- no platform is treated as authoritative
- all imported data becomes attestations
- signatures required where possible
- unverifiable data is weighted conservatively
- users control which integrations they enable

---

## Summary
Integrations expand BitRep’s trust graph by incorporating verifiable signals from external platforms while maintaining decentralization and user control.
