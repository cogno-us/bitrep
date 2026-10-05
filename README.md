> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# BitRep — Verifiable, Portable Binary Attestations

BitRep is a protocol and reference implementation for **verifiable trust** built on cryptographic identity, binary attestations, and decentralized governance. It provides a trust layer that is **portable**, **auditable**, and **independent** of any single platform.

## Features
- **[self‑sovereign identity](guide://action?prefill=Tell%20me%20more%20about%3A%20self%E2%80%91sovereign%20identity)** — RSA keypairs with verification endpoints  
- **[binary attestations](guide://action?prefill=Tell%20me%20more%20about%3A%20binary%20attestations)** — signed, anchored trust statements (issuer → subject)  
- **[governance](guide://action?prefill=Tell%20me%20more%20about%3A%20governance)** — one-identity-one-vote proposals and voting  
- **[privacy layer](guide://action?prefill=Tell%20me%20more%20about%3A%20privacy%20layer)** — ZK framework and selective disclosure of attestations  
- **[integrations](guide://action?prefill=Tell%20me%20more%20about%3A%20integrations)** — import attestations from GitHub, eBay, LinkedIn, StackOverflow  
- **[security](guide://action?prefill=Tell%20me%20more%20about%3A%20security)** — explicit issuer-key trust and v1 Ed25519 verification
- **[testing](guide://action?prefill=Tell%20me%20more%20about%3A%20testing)** — full FastAPI test suite

## Why BitRep Exists
Online trust is fragmented across platforms. BitRep provides a **shared attestation layer** that applications can adopt without centralizing trust or locking users into a single ecosystem.

## How It Works
- **[Identity](guide://action?prefill=Tell%20me%20more%20about%3A%20Identity):** users generate RSA keypairs; public keys act as decentralized identifiers.  
- **[Attestations](guide://action?prefill=Tell%20me%20more%20about%3A%20Attestations):** identities issue signed, binary statements about others. Each attestation carries: `{issuer, subject, attestation_type, signature, timestamp, anchor}`.  
- **[Governance](guide://action?prefill=Tell%20me%20more%20about%3A%20Governance):** proposals use one-identity-one-vote rather than tokens or weighted scores.  
- **[Privacy](guide://action?prefill=Tell%20me%20more%20about%3A%20Privacy):** threshold and selective-disclosure generators are demonstrations only; HTTP proof endpoints are disabled.

## Attestation Model
BitRep attestations are **binary, signed, anchored statements**. There is no numeric reputation score, no aggregation, and no scoring formula. Each attestation contains:

| Field | Description |
|---|---|
| `issuer` | Identity issuing the attestation |
| `subject` | Identity the attestation is about |
| `attestation_type` | Type of attestation (e.g., `"peer_verified"`) |
| `signature` | Cryptographic signature from issuer |
| `timestamp` | When the attestation was created |
| `anchor` | Optional anchor (e.g., transaction hash, mutual validation) |

## Quick Start
- **[install dependencies](guide://action?prefill=Tell%20me%20more%20about%3A%20install%20dependencies)**  
- **[run the FastAPI server](guide://action?prefill=Tell%20me%20more%20about%3A%20run%20the%20FastAPI%20server)**  
- **[generate an identity](guide://action?prefill=Tell%20me%20more%20about%3A%20generate%20an%20identity)**  
- **[issue an attestation](guide://action?prefill=Tell%20me%20more%20about%3A%20issue%20an%20attestation)**  
- **[query attestations](guide://action?prefill=Tell%20me%20more%20about%3A%20query%20attestations)**  

## API Overview
- **[identity endpoints](guide://action?prefill=Tell%20me%20more%20about%3A%20identity%20endpoints)** — legacy identity creation; trusted-key provisioning/rotation is operator managed
- **[attestation endpoints](guide://action?prefill=Tell%20me%20more%20about%3A%20attestation%20endpoints)** — issue, validate, list  
- **[governance endpoints](guide://action?prefill=Tell%20me%20more%20about%3A%20governance%20endpoints)** — proposals, votes, tallies  

## Security Notes
- **[RSA signatures](guide://action?prefill=Tell%20me%20more%20about%3A%20RSA%20signatures)**  
- **[input validation](guide://action?prefill=Tell%20me%20more%20about%3A%20input%20validation)**  
- **[documented threat model](guide://action?prefill=Tell%20me%20more%20about%3A%20documented%20threat%20model)**  
- **[experimental ZK framework](guide://action?prefill=Tell%20me%20more%20about%3A%20experimental%20ZK%20framework)** (not production‑grade)

## Contributing
Contributions are welcome in:
- **[cryptography](guide://action?prefill=Tell%20me%20more%20about%3A%20cryptography)**  
- **[backend engineering](guide://action?prefill=Tell%20me%20more%20about%3A%20backend%20engineering)**  
- **[governance design](guide://action?prefill=Tell%20me%20more%20about%3A%20governance%20design)**  
- **[privacy systems](guide://action?prefill=Tell%20me%20more%20about%3A%20privacy%20systems)**  

Open an issue, start a discussion, or submit a PR.
