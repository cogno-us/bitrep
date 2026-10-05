> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# BitRep Protocol Specification

This document defines the BitRep protocol: identities, attestations, reputation computation, and governance primitives. It is implementation‑agnostic and describes the canonical behavior expected across all conforming clients and services.

## 1. Identity

### 1.1 Keypairs
- RSA‑2048 keypairs generated client‑side.
- Public key = decentralized identifier (DID).
- Private key never leaves the client.

### 1.2 Identity Document
Each identity exposes:
- public_key
- created_at
- optional metadata (non‑authoritative)

### 1.3 Key Rotation
Identities may rotate keys by issuing:
- a signed rotation statement from the old key
- a confirmation signature from the new key

Reputation transfers automatically.

---

## 2. Attestations

### 2.1 Structure
An attestation contains:
- issuer_public_key
- subject_public_key
- weight (float, bounded)
- timestamp
- signature(issuer_private_key, payload)

### 2.2 Validity Rules
- signature must match issuer_public_key
- timestamp must be within acceptable skew
- weight must be within protocol bounds
- issuer and subject may not be identical

### 2.3 Revocation
Attestations may be revoked by:
- issuer signature over a revocation statement
- expiration (optional, implementation‑specific)

---

## 3. Reputation

### 3.1 Trust Graph
Directed, weighted graph:
- nodes = identities
- edges = attestations

### 3.2 Propagation Algorithm
Modified PageRank:
- damping factor
- issuer‑credibility weighting
- normalization to prevent Sybil inflation

### 3.3 Output
- raw score (float)
- score band (coarse category)
- optional proof inputs for ZK layer

---

## 4. Governance

### 4.1 Proposals
A proposal includes:
- proposal_id
- creator_public_key
- metadata
- deadline
- signature

### 4.2 Voting
- votes weighted by reputation score
- quadratic scaling applied
- deterministic tally

### 4.3 Finalization
A proposal is finalized when:
- deadline passes
- tally is computed
- result is signed by the service

---

## 5. Privacy Layer (Experimental)

### 5.1 ZK Threshold Proofs
Users may prove:
- “my reputation ≥ X”
without revealing raw score.

### 5.2 Limitations
- not production‑grade
- not resistant to advanced inference attacks

---

## 6. Compatibility

### 6.1 Required Behaviors
All implementations must:
- validate signatures
- enforce attestation rules
- compute reputation deterministically

### 6.2 Optional Extensions
- additional attestation sources
- custom governance modules
- alternative cryptographic primitives

---

## 7. Summary
This specification defines the canonical BitRep protocol. Implementations must follow these rules to ensure interoperability, determinism, and verifiable reputation across platforms.
