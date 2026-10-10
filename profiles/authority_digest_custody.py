"""Optional non-authorizing authority policy/grant digest-custody profile.

This module composes the accepted BitRep v1 verifier without changing it. A
successful result authenticates two independently configured signatures over
bounded digest-custody records. It never establishes lawful institutional
authority or grants action permission.
"""
import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, model_validator

from models.verification import AttestationEnvelope, Epoch, StrictModel, Token
from utils.trust import TrustRegistry, TrustUnavailable
from utils.verification import verify_attestation

DIGEST = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
CLAIM_DOMAIN = b"Cognous authority digest custody v1\n"
WITNESS_DOMAIN = b"Cognous authority digest witness v1\n"


class AuthorityDigestClaim(StrictModel):
    """Bounded digest metadata; it is evidence input, not an authority grant."""

    profile_version: Literal["authority-digest-custody/1"] = "authority-digest-custody/1"
    authority_kind: Literal["policy", "grant"]
    authority_id: Token
    authority_epoch: Annotated[int, Field(ge=1, le=9007199254740991)]
    authority_digest: DIGEST
    effective_from: Epoch
    effective_until: Epoch
    observed_at: Epoch
    publisher_ref: Token
    witness_ref: Token

    @model_validator(mode="after")
    def bounded_times_and_independence(self) -> "AuthorityDigestClaim":
        if not self.effective_from < self.effective_until:
            raise ValueError("effective interval must be non-empty")
        if not self.effective_from <= self.observed_at < self.effective_until:
            raise ValueError("observed_at must fall inside the effective interval")
        if self.publisher_ref == self.witness_ref:
            raise ValueError("publisher and witness must be distinct")
        return self


class WitnessCommitment(StrictModel):
    """What the independent witness signs through a normal v1 attestation."""

    profile_version: Literal["authority-digest-witness/1"] = "authority-digest-witness/1"
    authority_claim_digest: DIGEST
    publisher_statement_digest: DIGEST
    publisher_trust_snapshot: DIGEST
    authority_digest: DIGEST
    authority_epoch: Annotated[int, Field(ge=1, le=9007199254740991)]
    observed_at: Epoch
    publisher_ref: Token
    witness_ref: Token


class CustodyVerification(StrictModel):
    """Local profile result. `accepted` is digest-custody acceptance only."""

    result_version: Literal["authority-digest-custody-result/1"] = (
        "authority-digest-custody-result/1"
    )
    accepted: bool
    reason: str
    assurance: Literal["non_authorizing_digest_custody", "none"]
    authority_digest: DIGEST
    authority_epoch: Annotated[int, Field(ge=1, le=9007199254740991)]
    publisher_statement_digest: DIGEST | None = None
    publisher_trust_snapshot: DIGEST | None = None
    witness_statement_digest: DIGEST | None = None
    witness_trust_snapshot: DIGEST | None = None


def _canonical(domain: bytes, value: StrictModel) -> bytes:
    return domain + json.dumps(
        value.model_dump(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical_claim_bytes(claim: AuthorityDigestClaim) -> bytes:
    return _canonical(CLAIM_DOMAIN, claim)


def claim_digest(claim: AuthorityDigestClaim) -> str:
    return _sha256(canonical_claim_bytes(claim))


def canonical_witness_bytes(commitment: WitnessCommitment) -> bytes:
    return _canonical(WITNESS_DOMAIN, commitment)


def witness_digest(commitment: WitnessCommitment) -> str:
    return _sha256(canonical_witness_bytes(commitment))


def _result(
    claim: AuthorityDigestClaim,
    reason: str,
    publisher_result=None,
    witness_result=None,
) -> CustodyVerification:
    accepted = reason == "ok"
    return CustodyVerification(
        accepted=accepted,
        reason=reason,
        assurance="non_authorizing_digest_custody" if accepted else "none",
        authority_digest=claim.authority_digest,
        authority_epoch=claim.authority_epoch,
        publisher_statement_digest=getattr(publisher_result, "statement_digest", None),
        publisher_trust_snapshot=getattr(publisher_result, "trust_snapshot", None),
        witness_statement_digest=getattr(witness_result, "statement_digest", None),
        witness_trust_snapshot=getattr(witness_result, "trust_snapshot", None),
    )


def verify_authority_digest_custody(
    *,
    authority_bytes: bytes,
    claim: AuthorityDigestClaim,
    publisher_attestation: AttestationEnvelope,
    publisher_trust: TrustRegistry,
    witness_attestation: AttestationEnvelope | None,
    witness_trust: TrustRegistry | None,
    expected_epoch: int,
    now: int,
) -> CustodyVerification:
    """Verify bounded digest custody under two explicit independent snapshots.

    The caller supplies current trusted snapshots and trusted current time. The
    function neither discovers trust nor issues/validates institutional grants.
    """
    if expected_epoch != claim.authority_epoch:
        return _result(claim, "wrong_epoch")
    if _sha256(authority_bytes) != claim.authority_digest:
        return _result(claim, "authority_digest_mismatch")

    pub = publisher_attestation.statement
    if pub.issuer != claim.publisher_ref:
        return _result(claim, "publisher_identity_mismatch")
    if pub.subject != claim.authority_id or pub.statement_type != "authority_digest_publisher":
        return _result(claim, "publisher_scope_mismatch")
    if pub.content_digest != claim_digest(claim):
        return _result(claim, "publisher_content_digest_mismatch")
    if pub.issued_at != claim.observed_at:
        return _result(claim, "publisher_observed_time_mismatch")

    try:
        publisher_result = verify_attestation(publisher_attestation, publisher_trust, now)
    except TrustUnavailable:
        return _result(claim, "publisher_trust_not_current")
    if publisher_result.outcome != "verified":
        return _result(claim, "publisher_" + publisher_result.reason, publisher_result)

    if witness_attestation is None or witness_trust is None:
        return _result(claim, "missing_witness", publisher_result)
    if publisher_trust.fingerprint() == witness_trust.fingerprint():
        return _result(claim, "non_independent_trust_snapshots", publisher_result)
    if any(key.issuer == claim.witness_ref for key in publisher_trust.keys):
        return _result(claim, "witness_present_in_publisher_trust", publisher_result)
    if any(key.issuer == claim.publisher_ref for key in witness_trust.keys):
        return _result(claim, "publisher_present_in_witness_trust", publisher_result)

    commitment = WitnessCommitment(
        authority_claim_digest=claim_digest(claim),
        publisher_statement_digest=publisher_result.statement_digest,
        publisher_trust_snapshot=publisher_result.trust_snapshot,
        authority_digest=claim.authority_digest,
        authority_epoch=claim.authority_epoch,
        observed_at=claim.observed_at,
        publisher_ref=claim.publisher_ref,
        witness_ref=claim.witness_ref,
    )
    wit = witness_attestation.statement
    if wit.issuer != claim.witness_ref:
        return _result(claim, "witness_identity_mismatch", publisher_result)
    if wit.subject != publisher_result.statement_digest or wit.statement_type != "authority_digest_witness":
        return _result(claim, "witness_scope_mismatch", publisher_result)
    if wit.content_digest != witness_digest(commitment):
        return _result(claim, "witness_content_digest_mismatch", publisher_result)
    if wit.issued_at < claim.observed_at:
        return _result(claim, "witness_backdated", publisher_result)

    try:
        witness_result = verify_attestation(witness_attestation, witness_trust, now)
    except TrustUnavailable:
        return _result(claim, "witness_trust_not_current", publisher_result)
    if witness_result.outcome != "verified":
        return _result(
            claim, "witness_" + witness_result.reason, publisher_result, witness_result
        )

    return _result(claim, "ok", publisher_result, witness_result)
