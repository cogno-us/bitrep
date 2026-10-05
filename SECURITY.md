> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# Security Policy

BitRep handles identity, attestations, reputation scoring, and governance logic.  
Security is a core requirement for the project, and all vulnerability reports are taken seriously.

## Reporting a Vulnerability
Please **do not open public issues** for security concerns.

Instead, report vulnerabilities privately by email:

**security@bitrep.dev**  
(If this address is not yet active, use the maintainer’s GitHub‑associated email.)

Include:
- a clear description of the issue  
- steps to reproduce  
- affected components  
- any relevant logs or payloads  

You will receive an acknowledgment within 72 hours.

## Scope
The following components are in scope for security review:
- identity generation and verification  
- attestation creation, validation, and storage  
- reputation scoring logic  
- governance proposal and voting mechanisms  
- API endpoints and request validation  
- cryptographic operations (RSA signatures, hashing, verification)

## Out of Scope
The following are not considered security vulnerabilities:
- theoretical attacks without a reproducible vector  
- issues requiring unrealistic attacker capabilities  
- denial‑of‑service via excessive legitimate requests  
- third‑party platform behavior (GitHub, eBay, LinkedIn, StackOverflow)  
- experimental ZK components (see below)

## Cryptographic Assumptions
BitRep currently uses:
- RSA‑2048 for identity and attestation signatures  
- SHA‑256 for hashing  
- deterministic signature verification  
- no custom cryptography  

These primitives are standard, but the implementation should be reviewed by qualified cryptographers.

## Zero‑Knowledge Framework (Experimental)
The ZK framework included in BitRep is **not production‑grade**.  
It is intended for:
- selective disclosure experiments  
- threshold‑based reputation proofs  
- research and prototyping  

It should **not** be used for high‑assurance privacy guarantees.

## Threat Model Summary
BitRep assumes:
- attackers can create arbitrary identities  
- attackers can issue malicious attestations  
- attackers may attempt Sybil amplification  
- network traffic may be observable  
- storage may be partially compromised  

BitRep does **not** assume:
- trusted third‑party platforms  
- honest majority of identities  
- secure client devices  
- private network environments  

## Responsible Disclosure
If you discover a vulnerability:
- report privately  
- allow maintainers time to investigate  
- avoid public disclosure until a fix is available  

Thank you for helping keep BitRep secure.
