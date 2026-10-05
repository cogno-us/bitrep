> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# BitRep API Reference

This document describes the public API endpoints exposed by the BitRep FastAPI service.

Base URL:
http://localhost:8000

---

# 1. Identity Endpoints

## POST /identity/create
Generate a new identity keypair.
Response:
- public_key
- private_key (client must store securely)

## POST /identity/verify
Verify ownership of a public key via signature challenge.

## POST /identity/rotate
Rotate an identity’s keypair while preserving reputation.

---

# 2. Attestation Endpoints

## POST /attestations/issue
Issue a signed attestation.
Body:
- issuer_private_key
- subject_public_key
- weight

## POST /attestations/validate
Validate an attestation’s signature and structure.

## GET /attestations/list/{public_key}
List attestations issued about a given identity.

---

# 3. Reputation Endpoints

## POST /reputation/compute
Recompute global reputation scores.
Returns:
- raw scores
- score bands
- graph diagnostics

## GET /reputation/{public_key}
Retrieve reputation for a specific identity.

## GET /reputation/graph
Inspect trust graph structure (sanitized).

---

# 4. Governance Endpoints

## POST /governance/proposals/create
Create a new proposal.

## GET /governance/proposals/{proposal_id}
Retrieve proposal metadata.

## POST /governance/vote
Submit a signed vote.

## GET /governance/tally/{proposal_id}
Retrieve final tally.

---

# 5. Health & Utility

## GET /health
Service health check.

## GET /version
Return protocol and implementation version.

---

# Summary
This API provides full access to identity, attestation, reputation, and governance functionality. All write operations require valid signatures; all read operations are public.
