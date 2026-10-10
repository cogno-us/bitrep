# Authority Digest Custody Profile v1

Status: bounded optional proposal for issue #10. This profile is **non-authorizing**. It composes the accepted `bitrep-attestation/1` verifier as an issuer-authentication primitive and does not alter that verifier, enroll a trust root, issue a grant, or claim that existing BitRep deployments sign Authority Context policies.

## Purpose

A mutable policy store can rewrite both policy text and a colocated digest. That digest is therefore not an independent custody boundary. This profile defines a small verification contract in which:

- an **authority publisher** signs a digest-custody claim under an explicit publisher trust snapshot;
- a separately identified **witness** signs a commitment to the publisher statement and publisher trust-snapshot fingerprint under a separate explicit witness trust snapshot;
- a consumer compares the claimed authority digest with the exact policy or grant bytes it is evaluating;
- epoch, effective interval and observed time are explicit inputs; and
- successful verification means only `non_authorizing_digest_custody`.

The profile authenticates custody assertions. It does not decide whether the referenced policy or grant was lawfully adopted, remains institutionally valid, applies to the caller, or authorizes an effect.

## Roles and separation

| Role | Profile responsibility | Not implied |
|---|---|---|
| Policy editor | May author or store policy/grant bytes | Cannot refresh independent custody signatures merely by rewriting text and a colocated digest |
| Authority publisher | Signs the digest-custody claim | Is not made a grant issuer by this profile |
| Decision writer | May consume a verified custody result | Cannot convert authentication into lawful authority |
| Independent witness | Signs a commitment to the publisher statement and publisher trust snapshot | Does not approve the policy/grant or the downstream decision |
| Relying verifier | Supplies current trusted time, expected epoch and two explicit trust snapshots | Does not discover trust or mint credentials |

The bounded profile requires `publisher_ref != witness_ref`, distinct trust-snapshot fingerprints, and no cross-enrollment of the witness issuer in the publisher snapshot or publisher issuer in the witness snapshot. These checks are conservative synthetic independence checks, not proof of organizational independence.

## Claim schema

`AuthorityDigestClaim` is the canonical profile payload. The JSON Schema is `authority-digest-custody-v1.schema.json`.

Required fields:

- `profile_version`: exactly `authority-digest-custody/1`.
- `authority_kind`: `policy` or `grant`.
- `authority_id`: stable caller-agreed identifier.
- `authority_epoch`: positive integer generation expected by the relying verifier.
- `authority_digest`: SHA-256 of the exact authority bytes consumed downstream.
- `effective_from`, `effective_until`: non-empty effective interval.
- `observed_at`: claimed publisher observation time, which must fall inside the effective interval.
- `publisher_ref`, `witness_ref`: distinct issuer identities expected by the profile.

Canonical claim bytes are the ASCII domain `Cognous authority digest custody v1\n` followed by compact lexicographically sorted JSON. The publisher's normal BitRep v1 statement uses:

- `issuer == publisher_ref`;
- `subject == authority_id`;
- `statement_type == authority_digest_publisher`;
- `content_digest == SHA256(canonical claim bytes)`; and
- `issued_at == observed_at`.

The profile then constructs `WitnessCommitment`, which binds the claim digest, publisher statement digest, publisher trust-snapshot fingerprint, authority digest, epoch, observed time and both role references. Canonical witness bytes use domain `Cognous authority digest witness v1\n`. The witness's BitRep v1 statement uses:

- `issuer == witness_ref`;
- `subject == publisher statement digest`;
- `statement_type == authority_digest_witness`; and
- `content_digest == SHA256(canonical witness bytes)`.

The witness statement must not predate `observed_at`.

## Verification order

The reference profile verifier fails closed in this order:

1. expected epoch matches the claim;
2. exact authority bytes hash to `authority_digest`;
3. publisher issuer, scope, claim digest and observed time match;
4. publisher attestation verifies under the supplied current publisher trust snapshot;
5. a witness and witness trust snapshot are present;
6. publisher and witness trust configuration satisfies the bounded independence checks;
7. witness issuer, scope and witness commitment digest match;
8. witness is not backdated before the publisher observation;
9. witness attestation verifies under the supplied current witness trust snapshot.

The accepted BitRep verifier retains its existing conservative revocation behavior. Revoked keys and stale/future trust snapshots therefore fail the custody profile closed.

## Threat cases covered by synthetic tests

`tests/test_authority_digest_custody_profile.py` exercises:

- a valid `policy` and valid `grant` digest-custody case;
- a policy editor rewriting both authority bytes and the colocated digest without independent publisher/witness signatures;
- forged publisher issuer identity;
- revoked publisher key;
- stale publisher trust snapshot;
- wrong authority epoch;
- missing witness;
- a witness signature whose issuance time predates the publisher observation; and
- an `observed_at` value outside the effective interval.

All keys in tests are ephemeral synthetic keys created inside the test process. No real secret, credential or production trust root is included.

## Trust and time limits

`observed_at` and the publisher/witness issuance times are signed assertions. The profile does **not** provide a trusted timestamp authority, external transparency log, durable snapshot archive or historical as-of verification. An issuer controlling a still-valid signing key can make a signed claim about an earlier time within the verifier's accepted key interval. The profile only detects the specified structural backdating cases and relies on caller-supplied trusted current time plus the accepted v1 current-state key rules.

The trust-snapshot fingerprint used by the accepted verifier is a local digest of operator-supplied trust configuration; it is not itself an externally signed registry receipt. The separate publisher/witness snapshots in this profile are explicit inputs, not newly introduced production trust roots.

## Authority boundary

A successful result has `assurance = non_authorizing_digest_custody`. It establishes only that, at the supplied evaluation time and under the two supplied trust snapshots, the exact authority bytes matched the claimed digest and the two configured issuers authenticated the bounded publisher/witness commitments.

It does **not** establish:

- lawful adoption or institutional validity of a policy;
- issuance, validity or applicability of a grant;
- actor permission, target/payload authorization or destination commit atomicity;
- factual truth of the underlying authority text;
- independent organizational control merely because issuer identifiers differ; or
- production key custody, secure time, anti-rollback snapshot distribution or incident response.

Those remain responsibilities of the relevant institutional authority, control-plane and deployment contracts.
