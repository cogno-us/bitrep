# Proposed cross-component contract pending Governor review

Status: implemented BitRep reference interface; cross-component adoption is **proposed**, not approved. No changes to The Index, ODES or other repositories. This is not a production-readiness claim.

## Responsibility

BitRep checks a binary assertion's signature and its admissibility under an explicitly configured issuer-key trust snapshot. `verified` means **issuer signature only**, under that snapshot at the stated evaluation time. It does not establish factual truth, content availability, institutional authority, action permission, source independence, blockchain inclusion or a reputation score. Evidence weighting and claim interpretation belong downstream.

## Wire input and canonical signed bytes

`POST /verify` checks without storing; `POST /attest` checks before admission. Both take exactly `{ "statement": {...}, "signature": "..." }`. JSON objects with duplicate members, unknown fields, malformed values, coercible types, invalid time order or bodies exceeding 16,384 bytes are rejected. No caller key, proof, evaluation time or trust snapshot is accepted. See executable Pydantic models in `models/verification.py` and JSON Schema files alongside this document.

Every statement field below is mandatory and signed:

| Field | v1 rule |
|---|---|
| `protocol_version` | Exactly `bitrep-attestation/1` |
| `algorithm` | Exactly `Ed25519`; no algorithm negotiation/fallback |
| `attestation_id` | Issuer-scoped identifier retained across legitimate retries |
| `issuer`, `key_id` | Exact tuple in the operator trust snapshot |
| `subject` | Stable downstream claim/evidence/subject identifier |
| `statement_type` | Opaque application-defined binary assertion type; no score |
| `audience` | Must equal the configured deployment/consumer audience |
| `content_digest` | `sha256:` followed by 64 lowercase hexadecimal digits; hash of exact external content/evidence bytes |
| `issued_at`, `not_before`, `expires_at` | Strict integer Unix UTC seconds, 0..2^53-1; `issued_at <= not_before < expires_at` |

All identifier/string fields except the digest are 1..256 visible ASCII characters (U+0021..U+007E). Consumers with Unicode content hash its agreed exact bytes; non-ASCII identifiers require a separate agreed encoding. No case folding, Unicode normalization or timestamp rewriting occurs.

Canonical signed bytes are the ASCII prefix `BitRep attestation v1\n` (the last byte is LF), followed immediately by the statement serialized as compact JSON with lexicographically sorted keys, standard JSON string escaping and no whitespace or trailing newline. The input domain has no floats, Unicode, nested objects or optional statement fields. Python reference: `canonical_bytes(statement)` in `utils/verification.py`. This is a **restricted v1 serialization**, not a claim of general RFC 8785/JCS support. Outer JSON whitespace and member order do not affect verification. Signature is excluded from signed bytes and is canonical padded standard Base64 of the 64-byte Ed25519 signature.

`statement_digest = "sha256:" + SHA256(canonical_signed_bytes).hexdigest()` identifies the complete signed statement. It differs from `content_digest`. Consumers must compare `content_digest` with the content bytes they actually use; BitRep does not fetch or validate those external bytes. Any evidence encoding or manifest of multiple artifacts is a downstream profile decision.

## Trust configuration and timing

Set `BITREP_TRUST_REGISTRY` to an operator-controlled local JSON file. The service reloads it on every request; absence, invalid contents or expired/future snapshot fails closed with HTTP 503. No default trusted issuer exists. Public identity registration and legacy `verified` database flags do not establish trust.

Snapshot format: `registry_version: "bitrep-trust/1"`, `audience`, `published_at`, `valid_until`, and `keys`. Each key has `issuer`, `key_id`, Base64 raw 32-byte Ed25519 `public_key`, `valid_from`, `valid_until`, and optional `revoked_at` (integer or null). Tuple duplicates invalidate the snapshot. The server's current time must be in `[published_at, valid_until)`. `trust_snapshot` in results is the SHA-256 of compact sorted JSON of the validated snapshot (including null defaults), not an externally authenticated registry signature.

Implemented policy:

- Key must be valid **both at signed issuance and at current evaluation**. Current interval and issuance interval are `[valid_from, valid_until)`.
- Current time must be at or after both `issued_at` and `not_before`, and strictly before `expires_at`. There is no clock-skew allowance.
- Once `now >= revoked_at`, all signatures using that key are rejected, including statements issued before revocation. This conservative policy prevents attacker-selected backdating from bypassing revocation.
- Rotation adds a new `(issuer, key_id)` record. Keep the old key only for its intended overlap interval. Never replace key material behind an existing ID. Expiry/revocation retires old keys; the implementation accepts overlapping active keys.
- Reads and duplicate submissions re-evaluate against current time and current trust. A historical admission remains stored when it later expires or is revoked, but its current `verification` becomes rejected.

Deployment requirements, **not implemented guarantees**: vetted issuer enrollment/identity binding, controlled file permissions, atomic snapshot replacement, prompt revocation distribution, a maximum allowed snapshot lifetime, secure clock, durable snapshot archives, audit of changes and anti-rollback protection across restarts. The service validates snapshot lifetime but cannot detect an operator replaying an older still-valid snapshot. The request uses one captured snapshot/time; it cannot promise globally instantaneous revocation during a concurrent update. Protect database writes from untrusted actors.

Historical verification is **not supported** as a caller-selectable as-of decision. `verification_at_acceptance` is an unsigned record of what this service concluded then, using its stored snapshot digest; it is not proof of signing time or current validity. Retain independently trusted timestamp/receipt evidence and archived snapshots before proposing a historical-verification profile. Current compromise revocation intentionally does not grandfather earlier signatures.

## Outcomes and errors

Well-formed `POST /verify` returns HTTP 200 with a versioned result, even when rejected. `POST /attest` returns 201 for new acceptance, 200 for idempotent resubmission, 422 for verification rejection and 409 for a validly signed issuer/ID conflict. Neither verification nor rejected admission writes accepted storage.

Verification-result fields:

| Field | Meaning |
|---|---|
| `result_version` | `bitrep-verification/1` |
| `outcome` | `verified` or `rejected` |
| `reason` | One code below; `ok` is the sole successful code |
| `evaluated_at`, `key_status_at` | Server time used for this current-state evaluation |
| `statement_digest` | Commitment to all canonical signed bytes |
| `trust_snapshot` | Fingerprint of the configured snapshot used |
| `assurance` | `issuer_signature_only` on success; otherwise `none` |

Verification rejection codes: `unsupported_version`, `unsupported_algorithm`, `audience_mismatch`, `unknown_key` (including an issuer/key mismatch), `key_revoked`, `key_not_yet_valid`, `key_expired`, `issuance_outside_key_validity`, `not_yet_valid`, `attestation_expired`, `malformed_signature`, `invalid_signature`. Invalid Base64 may be classified `invalid_signature`; neither category admits storage. Policy checks precede cryptographic verification, so rejection does not imply that a signature was evaluated.

Transport/configuration errors use `{"detail":{"reason":"..."}}`: `malformed_input` (422), `input_too_large` (413), `trust_unavailable` (503), `attestation_id_conflict` (409), `not_found` (404). They are not successful verification results. An HTTP 503 is not a negative conclusion about the underlying claim. Consumers must treat unknown versions, reasons, missing results, malformed responses and transport failures as **no usable assurance**.

`POST /attest` success: `{ "admission": "accepted" | "duplicate", "accepted_at": <original server time>, "verification": <current result> }`.

`GET /attestations/{statement_digest}` and `GET /user/{subject}` expose v1 admissions only. Each record includes `attestation`, `accepted_at`, `verification_at_acceptance` and freshly evaluated `verification`. A record's presence is not a current assurance result. Do not consume legacy `/integration` records or identity flags as this contract.

Results are **not signed portable receipts**. Consume them over an authenticated service channel, or invoke the verifier locally with a trusted snapshot. A copied JSON result is not independently authenticated; bind it to the expected statement digest and audience. Signed receipt transport and cross-component service authentication remain Governor/deployment decisions.

## Duplicate/replay rules and persistence

Accepted records live in `accepted_attestations_v1`, isolated from legacy `attestations`. The database enforces a primary key on `statement_digest` and uniqueness on `(issuer, attestation_id)`. API code verifies before any insert; a database uniqueness race is rolled back and resolved as duplicate or conflict.

Same issuer/ID and same canonical statement, with a currently valid signature: duplicate success, one stored record, original `accepted_at`. Same issuer/ID with a different validly signed statement: conflict, no write. Tampered, expired or revoked retries: rejection even if a prior admission exists. No API mutates/deletes an accepted record. Database administrator access is outside that boundary; this is not immutable/tamper-proof storage.

Different signed IDs with identical evidence are distinct assertions, **not independent evidence**. Preventing semantic duplication, coordinated issuers or downstream double-counting belongs to The Index. Audience binding prevents reuse across differently configured audiences. This is evidence ingestion, not a one-time action authorization token.

## Example and executable vectors

`tests/fixtures/verification-v1.json` is a complete synthetic record, public key, canonical byte string, digest and expected result at Unix time 1800000000. Its test seed is explicitly public; never deploy it. `tests/test_verification.py` checks the vector and real signing/verification.

Compact shape (placeholders are not executable signatures):

```json
{"statement":{"protocol_version":"bitrep-attestation/1","algorithm":"Ed25519","attestation_id":"test-001","issuer":"issuer:alice","key_id":"key:1","subject":"claim:42","statement_type":"asserts","audience":"index:test","content_digest":"sha256:<64 lowercase hex>","issued_at":1799999990,"not_before":1799999990,"expires_at":1800000100},"signature":"<Base64 Ed25519 signature>"}
```

```json
{"result_version":"bitrep-verification/1","outcome":"verified","reason":"ok","evaluated_at":1800000000,"key_status_at":1800000000,"statement_digest":"sha256:<signed-statement digest>","trust_snapshot":"sha256:<snapshot digest>","assurance":"issuer_signature_only"}
```

## Privacy and other unsupported assurance

The demonstration threshold hash and selective-disclosure helpers prove no underlying proposition. Their verification functions always return false. All three `/privacy/*` proof endpoints return 501 with `assurance: none`. External identity verification and third-party promotion endpoints also return 501. No demonstration helper feeds v1 accepted storage. Generators remain local demonstration utilities only.

No real ZK, Merkle membership verification, external platform verification, timestamp authority, blockchain anchor validation, factual adjudication, authorization, evidence weighting, signed result receipts or historical as-of verification is implemented by this contract.

## Migration and Governor decisions

1. Back up storage. Create the additive `accepted_attestations_v1` table (ORM startup or SQL schema); do not copy legacy rows into it. Legacy data remains preserved and unverified.
2. Provision vetted Ed25519 public keys and a current trust snapshot out of band. Legacy RSA helper signatures, unsigned submissions and old `AttestationIn` are not accepted by v1. Obtain fresh issuer-signed v1 statements; do not fabricate missing timestamps or commitments.
3. Update clients for strict envelopes, digest commitments and status codes. `/user` returns v1 contract records, not legacy `AttestationOut` rows. Privacy/placeholder verification clients must handle 501. Existing unsubstantiated identity/import flags remain historical data only and must not be trusted.
4. Configure authenticated transport, storage access controls, clock, snapshot rotation/revocation processes, archive retention and payload/rate limits before deployment. Existing governance/identity creation and integration surfaces remain prototypes, not an institutional authorization system.
5. Governor must approve the proposed versions and Ed25519 migration; designate issuer enrollment owners, audience/profile identifiers, content-byte conventions, snapshot freshness/rollback rules and downstream result-authentication requirements. Review the conservative revocation/expiry policy and explicitly scope any future historical proof profile.

The Index worker can begin **provisional adapter and synthetic conformance work** using this contract/vector. Production integration or reliance requires Governor approval and the deployment decisions above. The Index must recompute content commitments, check the expected subject/type/audience/digest, use current verification, and apply its own provenance, independence and weighting rules.
