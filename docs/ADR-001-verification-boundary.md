# ADR 001: Versioned admission with explicit issuer trust

Status: proposed cross-component contract pending Governor review; implemented locally in BitRep.

Canonical repository is `cogno-us/bitrep` (GitHub repository ID 1139951229). Both this URL and the report's older `bitrep-core/primary` URL resolve to that same ID. Starting default-branch commit: `572c00d5a6e73e74b383240a7f58c31c041b4174`. No AGENTS.md exists in that tree. CONTRIBUTING.md and SECURITY.md were inspected. History and MIT license are preserved; no new repository or visibility change.

Confirmed: `/attest` imported verification helpers but did not invoke them; supplied or absent signatures were stored. The privacy helpers accepted shapes rather than proving propositions. Existing tests expected unsigned acceptance and demonstration success. Those were not fixed upstream at the starting commit.

Decision: introduce an explicit Ed25519-only v1 envelope and operator-managed issuer-key snapshot; use a new accepted table so legacy records cannot silently inherit verified status. Preserve existing RSA utilities only for legacy use. Fail closed on demonstration and placeholder verification paths. Retain binary assertions with no numeric score or downstream authority logic.

Breaking changes are necessary because permissive unsigned ingestion cannot be made backward compatible with verified evidence. No automatic signature conversion or legacy promotion is possible. See VERIFICATION_CONTRACT_V1.md for migration, trust timing and exact interface.

Remaining boundaries: trust enrollment/distribution and anti-rollback, authenticated transport, signed portable receipts, durable historical trust evidence, external content retrieval, production hardening and independent cryptographic review. No claim of production readiness or full-stack interoperability.
