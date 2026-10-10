import base64
import hashlib
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from models.verification import AttestationEnvelope, SignedStatement
from profiles.authority_digest_custody import (
    AuthorityDigestClaim,
    WitnessCommitment,
    claim_digest,
    verify_authority_digest_custody,
    witness_digest,
)
from utils.trust import TrustRegistry
from utils.verification import canonical_bytes, statement_digest

NOW = 1800000000
AUDIENCE = "authority-digest:test"


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def trust(key, issuer: str, key_id: str) -> TrustRegistry:
    public = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return TrustRegistry.model_validate({
        "registry_version": "bitrep-trust/1",
        "audience": AUDIENCE,
        "published_at": NOW - 100,
        "valid_until": NOW + 1000,
        "keys": [{
            "issuer": issuer,
            "key_id": key_id,
            "public_key": base64.b64encode(public).decode(),
            "valid_from": NOW - 100,
            "valid_until": NOW + 1000,
            "revoked_at": None,
        }],
    })


def signed(key, issuer, key_id, subject, statement_type, digest, issued_at):
    statement = SignedStatement(
        protocol_version="bitrep-attestation/1",
        algorithm="Ed25519",
        attestation_id=f"{issuer}-{statement_type}-{issued_at}",
        issuer=issuer,
        key_id=key_id,
        subject=subject,
        statement_type=statement_type,
        audience=AUDIENCE,
        content_digest=digest,
        issued_at=issued_at,
        not_before=issued_at,
        expires_at=NOW + 100,
    )
    return AttestationEnvelope(
        statement=statement,
        signature=base64.b64encode(key.sign(canonical_bytes(statement))).decode(),
    )


def fixture(kind="policy", witness_time=NOW - 9):
    publisher_key = Ed25519PrivateKey.generate()
    witness_key = Ed25519PrivateKey.generate()
    raw = (
        b"policy-v3:refund-limit=1000"
        if kind == "policy"
        else b"grant-v3:refund<=1000"
    )
    claim = AuthorityDigestClaim(
        authority_kind=kind,
        authority_id=f"{kind}:refund-v3",
        authority_epoch=3,
        authority_digest=sha256(raw),
        effective_from=NOW - 50,
        effective_until=NOW + 200,
        observed_at=NOW - 10,
        publisher_ref="issuer:authority-publisher",
        witness_ref="issuer:independent-witness",
    )
    publisher_trust = trust(publisher_key, claim.publisher_ref, "key:publisher")
    witness_trust = trust(witness_key, claim.witness_ref, "key:witness")
    publisher = signed(
        publisher_key,
        claim.publisher_ref,
        "key:publisher",
        claim.authority_id,
        "authority_digest_publisher",
        claim_digest(claim),
        claim.observed_at,
    )
    commitment = WitnessCommitment(
        authority_claim_digest=claim_digest(claim),
        publisher_statement_digest=statement_digest(publisher.statement),
        publisher_trust_snapshot=publisher_trust.fingerprint(),
        authority_digest=claim.authority_digest,
        authority_epoch=claim.authority_epoch,
        observed_at=claim.observed_at,
        publisher_ref=claim.publisher_ref,
        witness_ref=claim.witness_ref,
    )
    witness = signed(
        witness_key,
        claim.witness_ref,
        "key:witness",
        statement_digest(publisher.statement),
        "authority_digest_witness",
        witness_digest(commitment),
        witness_time,
    )
    return raw, claim, publisher, publisher_trust, witness, witness_trust


def verify(values, expected_epoch=3, witness=True):
    raw, claim, publisher, publisher_trust, witness_attestation, witness_trust = values
    return verify_authority_digest_custody(
        authority_bytes=raw,
        claim=claim,
        publisher_attestation=publisher,
        publisher_trust=publisher_trust,
        witness_attestation=witness_attestation if witness else None,
        witness_trust=witness_trust if witness else None,
        expected_epoch=expected_epoch,
        now=NOW,
    )


@pytest.mark.parametrize("kind", ["policy", "grant"])
def test_valid_profile_is_explicitly_non_authorizing(kind):
    result = verify(fixture(kind))
    assert result.accepted
    assert result.reason == "ok"
    assert result.assurance == "non_authorizing_digest_custody"


def test_editor_rewriting_text_and_colocated_digest_fails_without_independent_signatures():
    raw, claim, publisher, publisher_trust, witness, witness_trust = fixture()
    rewritten = b"policy-v3:refund-limit=999999"
    rewritten_claim = claim.model_copy(update={"authority_digest": sha256(rewritten)})
    result = verify_authority_digest_custody(
        authority_bytes=rewritten,
        claim=rewritten_claim,
        publisher_attestation=publisher,
        publisher_trust=publisher_trust,
        witness_attestation=witness,
        witness_trust=witness_trust,
        expected_epoch=3,
        now=NOW,
    )
    assert not result.accepted
    assert result.reason == "publisher_content_digest_mismatch"


def test_forged_issuer_is_rejected():
    raw, claim, publisher, publisher_trust, witness, witness_trust = fixture()
    forged = AttestationEnvelope(
        statement=publisher.statement.model_copy(update={"issuer": "issuer:forged"}),
        signature=publisher.signature,
    )
    result = verify_authority_digest_custody(
        authority_bytes=raw,
        claim=claim,
        publisher_attestation=forged,
        publisher_trust=publisher_trust,
        witness_attestation=witness,
        witness_trust=witness_trust,
        expected_epoch=3,
        now=NOW,
    )
    assert result.reason == "publisher_identity_mismatch"


def test_revoked_publisher_key_is_rejected():
    values = list(fixture())
    data = values[3].model_dump()
    data["keys"][0]["revoked_at"] = NOW
    values[3] = TrustRegistry.model_validate(data)
    assert verify(tuple(values)).reason == "publisher_key_revoked"


def test_stale_trust_snapshot_fails_closed():
    values = list(fixture())
    data = values[3].model_dump()
    data["valid_until"] = NOW
    values[3] = TrustRegistry.model_validate(data)
    assert verify(tuple(values)).reason == "publisher_trust_not_current"


def test_wrong_epoch_and_missing_witness_fail_closed():
    values = fixture()
    assert verify(values, expected_epoch=4).reason == "wrong_epoch"
    assert verify(values, witness=False).reason == "missing_witness"


def test_backdated_witness_is_rejected():
    assert verify(fixture(witness_time=NOW - 11)).reason == "witness_backdated"


def test_backdated_observation_outside_effective_interval_is_schema_invalid():
    _, claim, *_ = fixture()
    data = claim.model_dump()
    data["observed_at"] = data["effective_from"] - 1
    with pytest.raises(ValidationError):
        AuthorityDigestClaim.model_validate(data)


def test_fixture_claim_matches_exact_synthetic_bytes():
    data = json.loads(Path("tests/fixtures/authority-digest-custody-v1.json").read_text())
    raw = data["authority_utf8"].encode()
    claim = AuthorityDigestClaim.model_validate(data["claim"])
    assert claim.authority_digest == sha256(raw)
    assert data["synthetic_only"] is True
