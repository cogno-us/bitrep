> **Implementation status:** The enforced attestation interface is the [proposed v1 verification contract](docs/VERIFICATION_CONTRACT_V1.md), pending Governor review. Legacy unsigned/RSA ingestion is not accepted. Demonstration privacy and placeholder identity/platform verification cannot establish assurance. Older examples and aspirational claims below do not describe v1 acceptance or production readiness.

# BitRep API Documentation

## Overview

BitRep is a peer-to-peer reputation system based on behavioral attestations with cryptographic signatures, weighted reputation calculations, governance mechanisms, privacy features, and third-party integrations.

## Core Features

### 1. Attestations
Create and manage behavioral attestations between users with cryptographic signatures.

#### Create Attestation
```http
POST /attest
Content-Type: application/json

{
  "from_user": "alice",
  "to_user": "bob",
  "value": 5,
  "context": "Delivered product on time",
  "signature": "optional_cryptographic_signature",
  "mutual_validation": "optional_mutual_validation_data"
}
```

Response:
```json
{
  "id": 1,
  "from_user": "alice",
  "to_user": "bob",
  "value": 5,
  "context": "Delivered product on time",
  "timestamp": "2026-01-23T05:00:00",
  "signature": null,
  "mutual_validation": null,
  "weight": 1.0
}
```

### 2. Identity Management

#### Create Identity
Generate a new identity with cryptographic key pair.

```http
POST /identity/create
Content-Type: application/json

{
  "username": "alice"
}
```

Response:
```json
{
  "username": "alice",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "message": "Store your private key securely. It cannot be recovered."
}
```

**Important**: Store the private key securely. It is returned only once and cannot be recovered.

#### Get Identity
```http
GET /identity/{username}
```

Response:
```json
{
  "username": "alice",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...",
  "verified": false,
  "reputation_score": 0.0
}
```

#### Verify Identity
```http
POST /identity/{username}/verify
Content-Type: application/json

{
  "verification_data": {}
}
```

### 3. User Reputation

#### Get User Reputation
Retrieves user reputation calculated using weighted PageRank algorithm.

```http
GET /user/{username}
```

Response:
```json
{
  "user": "bob",
  "reputation": 15.7,
  "attestations": [
    {
      "id": 1,
      "from_user": "alice",
      "to_user": "bob",
      "value": 5,
      "context": "Good work",
      "timestamp": "2026-01-23T05:00:00",
      "weight": 1.0
    }
  ]
}
```

### 4. Governance

#### Create Proposal
```http
POST /governance/proposal
Content-Type: application/json

{
  "title": "Improve reputation algorithm",
  "description": "Proposal to update PageRank parameters",
  "proposer": "alice",
  "days_until_expiry": 7
}
```

#### List Proposals
```http
GET /governance/proposals?status=active
```

#### Vote on Proposal
Votes are weighted by reputation using quadratic scaling.

```http
POST /governance/vote
Content-Type: application/json

{
  "proposal_id": 1,
  "voter": "alice",
  "support": 1
}
```

- `support`: 1 for yes, -1 for no

#### Finalize Proposal
```http
POST /governance/proposal/{proposal_id}/finalize
```

### 5. Privacy Features

#### Prove Reputation Threshold (Zero-Knowledge Proof)
Prove reputation exceeds a threshold without revealing exact score.

```http
POST /privacy/prove-threshold
Content-Type: application/json

{
  "username": "alice",
  "threshold": 50.0
}
```

Response:
```json
{
  "proof": "a1b2c3...",
  "threshold": 50.0,
  "verified": true
}
```

#### Verify Threshold Proof
```http
POST /privacy/verify-threshold
Content-Type: application/json

{
  "proof": "a1b2c3...",
  "threshold": 50.0,
  "verified": true
}
```

#### Get Reputation Band
Returns reputation in broad bands for privacy.

```http
GET /privacy/reputation-bands/{username}
```

Response:
```json
{
  "username": "alice",
  "reputation_band": "50-100",
  "message": "Reputation shown in bands for privacy"
}
```

#### Selective Disclosure
Create proof for specific attestations without revealing all.

```http
POST /privacy/selective-disclosure
Content-Type: application/json

{
  "username": "alice",
  "selected_indices": [0, 2, 5]
}
```

### 6. Third-Party Integration

#### List Supported Platforms
```http
GET /integration/platforms
```

Response:
```json
{
  "supported_platforms": {
    "github": {
      "name": "GitHub",
      "attestation_types": ["commits", "pull_requests", "reviews", "stars"],
      "description": "Import commit history and contribution data"
    },
    "ebay": {
      "name": "eBay",
      "attestation_types": ["seller_rating", "buyer_rating", "transactions"],
      "description": "Import transaction and rating history"
    }
  }
}
```

#### Import Third-Party Attestation
```http
POST /integration/import
Content-Type: application/json

{
  "username": "alice",
  "platform": "github",
  "platform_username": "alice_gh",
  "attestation_type": "commits",
  "value": 50.0,
  "metadata": {
    "repo_count": 10,
    "total_commits": 500
  }
}
```

#### Verify Third-Party Attestation
```http
POST /integration/verify/{attestation_id}
Content-Type: application/json

{
  "verification_proof": {}
}
```

#### Import GitHub Profile (Placeholder)
```http
POST /integration/github/import?username=alice&github_username=alice_gh
```

## Reputation Algorithm

BitRep uses a modified PageRank algorithm for weighted reputation calculation:

1. **Weighted Attestations**: Attestations from high-reputation users carry more weight
2. **Sybil Resistance**: Isolated clusters of mutual attestation are discounted
3. **Time Decay**: Recent attestations matter more (half-life: 365 days)
4. **Quadratic Scaling**: Voting power uses quadratic scaling to prevent plutocratic capture

### Reputation Weight Formula

```
weight = log2(1 + reputation) * cluster_discount
```

### Time Decay Formula

```
decay = e^(-age_days * ln(2) / half_life_days)
```

## Security

### Cryptographic Signatures
- RSA 2048-bit key pairs
- PSS padding with SHA-256
- Signature verification for attestations

### Identity Verification
- Self-sovereign identity model
- Cryptographic key ownership
- Multi-channel verification support

### Privacy
- Zero-knowledge proofs for threshold verification
- Selective attestation disclosure
- Reputation bands for privacy

## Development

### Running Tests
```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Test Coverage
- Cryptographic utilities: Key generation, signing, verification
- Reputation algorithms: PageRank, weighting, Sybil detection
- Zero-knowledge proofs: Threshold proofs, selective disclosure
- API endpoints: All major endpoints tested

### Starting the Server
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API documentation available at: http://localhost:8000/docs

## Architecture

### Models
- `AttestationModel`: Behavioral attestations with signatures
- `UserIdentityModel`: User identities with key pairs
- `GovernanceProposalModel`: Governance proposals
- `VoteModel`: Reputation-weighted votes
- `ThirdPartyAttestationModel`: External platform attestations

### Utilities
- `crypto.py`: Cryptographic key generation and signatures
- `reputation.py`: Weighted reputation calculation (PageRank)
- `zkproof.py`: Zero-knowledge proof generation and verification

### API Routers
- `/attest`: Attestation creation
- `/user`: User reputation queries
- `/identity`: Identity management
- `/governance`: Governance and voting
- `/privacy`: Privacy-preserving features
- `/integration`: Third-party platform integration
