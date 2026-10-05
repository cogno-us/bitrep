"""Adversarial HTTP/storage tests using real Ed25519 signatures."""
import base64
import copy
import json
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from sqlalchemy.exc import IntegrityError
from main import app
from api.attestations import get_trust, get_now
from models.attestation import AcceptedAttestationModel, AttestationModel
from models.identity import UserIdentityModel
from models.third_party import ThirdPartyAttestationModel
from models.verification import SignedStatement
from utils.trust import load_registry, TrustUnavailable
from utils.verification import canonical_bytes
from tests.conftest import NOW


def count(factory):
    with factory() as db:
        return db.query(AcceptedAttestationModel).count()


def reason(response):
    return response.json()['detail']['reason']


def test_accept_verify_and_retrieve(client, signed, session_factory):
    record = signed()
    checked = client.post('/verify', json=record)
    assert checked.json()['outcome'] == 'verified'
    assert count(session_factory) == 0
    response = client.post('/attest', json=record)
    assert response.status_code == 201
    assert count(session_factory) == 1
    result = response.json()['verification']
    assert result['assurance'] == 'issuer_signature_only'
    fetched = client.get('/attestations/' + result['statement_digest']).json()
    assert fetched['attestation'] == record
    assert fetched['verification'] == result
    with session_factory() as db:
        assert db.query(AttestationModel).count() == 0


@pytest.mark.parametrize('field,value', [
    ('content_digest', 'sha256:' + '0' * 64), ('subject', 'claim:other'),
    ('statement_type', 'denies'), ('attestation_id', 'stolen-id'),
    ('expires_at', NOW + 200), ('not_before', NOW - 1), ('issued_at', NOW - 20),
])
def test_signed_field_tampering(client, signed, session_factory, field, value):
    record = signed()
    record['statement'][field] = value
    response = client.post('/attest', json=record)
    assert response.status_code == 422
    assert reason(response) == 'invalid_signature'
    assert count(session_factory) == 0


@pytest.mark.parametrize('change,expected', [
    ({'issuer': 'issuer:mallory'}, 'unknown_key'),
    ({'key_id': 'unknown'}, 'unknown_key'),
    ({'protocol_version': 'bitrep-attestation/2'}, 'unsupported_version'),
    ({'algorithm': 'RSA'}, 'unsupported_algorithm'),
    ({'audience': 'other:deployment'}, 'audience_mismatch'),
    ({'expires_at': NOW}, 'attestation_expired'),
    ({'issued_at': NOW + 1, 'not_before': NOW + 1}, 'not_yet_valid'),
    ({'issued_at': NOW - 101}, 'issuance_outside_key_validity'),
])
def test_policy_rejection(client, signed, session_factory, change, expected):
    response = client.post('/attest', json=signed(**change))
    assert response.status_code == 422
    assert reason(response) == expected
    assert count(session_factory) == 0


def test_wrong_signer_and_issuer_substitution(client, signed, trust_data, session_factory):
    other = Ed25519PrivateKey.generate()
    record = signed()
    record['signature'] = base64.b64encode(other.sign(canonical_bytes(SignedStatement(**record['statement'])))).decode()
    assert reason(client.post('/attest', json=record)) == 'invalid_signature'
    trust_data['keys'].append({**trust_data['keys'][0], 'issuer': 'issuer:bob',
        'public_key': base64.b64encode(other.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()})
    record = signed(); record['statement']['issuer'] = 'issuer:bob'
    assert reason(client.post('/attest', json=record)) == 'invalid_signature'
    assert count(session_factory) == 0


@pytest.mark.parametrize('mutation', ['missing_issuer', 'missing_signature', 'extra_key', 'float_time',
    'bool_time', 'unicode', 'bad_digest', 'unordered_time', 'short_signature', 'legacy', 'null'])
def test_malformed_never_persists(client, signed, session_factory, mutation):
    record = signed()
    if mutation == 'missing_issuer': del record['statement']['issuer']
    elif mutation == 'missing_signature': del record['signature']
    elif mutation == 'extra_key': record['public_key'] = 'caller-trust-root'
    elif mutation == 'float_time': record['statement']['issued_at'] = float(NOW - 10)
    elif mutation == 'bool_time': record['statement']['issued_at'] = True
    elif mutation == 'unicode': record['statement']['subject'] = 'café'
    elif mutation == 'bad_digest': record['statement']['content_digest'] = 'sha256:no'
    elif mutation == 'unordered_time': record['statement']['expires_at'] = NOW - 20
    elif mutation == 'short_signature': record['signature'] = 'bad'
    elif mutation == 'legacy': record = {'issuer': 'alice', 'subject': 'bob', 'attestation_type': 'asserts'}
    elif mutation == 'null': record = None
    response = client.post('/attest', content=json.dumps(record))
    assert response.status_code == 422
    assert reason(response) == 'malformed_input'
    assert count(session_factory) == 0


@pytest.mark.parametrize('body', ['{"statement":{},"statement":{}}', '{oops', '{"x":NaN}', '\ud800'])
def test_ambiguous_or_invalid_json(client, session_factory, body):
    response = client.post('/attest', content=body.encode('utf-8', errors='surrogatepass'))
    assert response.status_code == 422
    assert count(session_factory) == 0


def test_oversize(client, session_factory):
    assert client.post('/attest', content=b' ' * 16385).status_code == 413
    assert count(session_factory) == 0


@pytest.mark.parametrize('signature', ['!' * 88, base64.b64encode(bytes(64)).decode()])
def test_invalid_signature(client, signed, session_factory, signature):
    record = signed(); record['signature'] = signature
    assert client.post('/attest', json=record).status_code == 422
    assert count(session_factory) == 0


def test_idempotence_and_id_conflict(client, signed, session_factory):
    record = signed()
    assert client.post('/attest', json=record).status_code == 201
    duplicate = client.post('/attest', json=record)
    assert duplicate.status_code == 200
    assert duplicate.json()['admission'] == 'duplicate'
    conflict = client.post('/attest', json=signed(subject='claim:conflict'))
    assert conflict.status_code == 409
    assert reason(conflict) == 'attestation_id_conflict'
    assert count(session_factory) == 1
    # A new signed ID is a new assertion, not independent evidence by definition.
    assert client.post('/attest', json=signed(attestation_id='test-002')).status_code == 201


@pytest.mark.parametrize('update,expected', [
    ({'revoked_at': NOW}, 'key_revoked'),
    ({'valid_until': NOW}, 'key_expired'),
    ({'valid_from': NOW + 1}, 'key_not_yet_valid'),
])
def test_key_lifecycle(client, signed, trust_data, session_factory, update, expected):
    trust_data['keys'][0].update(update)
    response = client.post('/attest', json=signed())
    assert reason(response) == expected
    assert count(session_factory) == 0


def test_revocation_rechecks_duplicates_and_reads(client, signed, trust_data, session_factory):
    record = signed()
    first = client.post('/attest', json=record).json()
    trust_data['keys'][0]['revoked_at'] = NOW
    assert reason(client.post('/attest', json=record)) == 'key_revoked'
    fetched = client.get('/attestations/' + first['verification']['statement_digest']).json()
    assert fetched['verification']['reason'] == 'key_revoked'
    assert fetched['verification_at_acceptance']['outcome'] == 'verified'
    assert count(session_factory) == 1


def test_expired_replay(client, signed, session_factory):
    record = signed()
    assert client.post('/attest', json=record).status_code == 201
    app.dependency_overrides[get_now] = lambda: NOW + 100
    assert reason(client.post('/attest', json=record)) == 'attestation_expired'
    assert count(session_factory) == 1


def test_rotation(client, signed, trust_data, signing_key, session_factory):
    other = Ed25519PrivateKey.generate()
    trust_data['keys'].append({**trust_data['keys'][0], 'key_id': 'key:2', 'public_key': base64.b64encode(
        other.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()})
    assert client.post('/attest', json=signed()).status_code == 201
    record = signed(key_id='key:2', attestation_id='rotated')
    assert reason(client.post('/attest', json=record)) == 'invalid_signature'
    record['signature'] = base64.b64encode(other.sign(canonical_bytes(SignedStatement(**record['statement'])))).decode()
    assert client.post('/attest', json=record).status_code == 201
    assert count(session_factory) == 2


def test_database_uniqueness(session_factory, client, signed):
    client.post('/attest', json=signed())
    with session_factory() as db:
        original = db.query(AcceptedAttestationModel).one()
        db.add(AcceptedAttestationModel(statement_digest='other', issuer=original.issuer,
            attestation_id=original.attestation_id, subject='other', envelope_json='{}',
            verification_json='{}', accepted_at=NOW))
        with pytest.raises(IntegrityError): db.commit()
        db.rollback()
    assert count(session_factory) == 1


def test_legacy_rows_not_promoted(client, session_factory):
    with session_factory() as db:
        db.add(AttestationModel(issuer='alice', subject='claim:42', attestation_type='asserts', signature='fake'))
        db.commit()
    assert client.get('/user/claim:42').json()['attestations'] == []
    assert count(session_factory) == 0


@pytest.mark.parametrize('path', ['/privacy/prove-threshold', '/privacy/verify-threshold', '/privacy/selective-disclosure',
    '/identity/alice/verify', '/integration/verify/1'])
def test_placeholder_cannot_assure(client, session_factory, path):
    response = client.post(path, json={'proof': 'a' * 64, 'threshold': 100, 'verified': True})
    assert response.status_code == 501
    assert count(session_factory) == 0


def test_self_created_identity_not_trusted(client, signed, session_factory):
    assert client.post('/identity/create', json={'username': 'issuer:mallory'}).status_code == 200
    assert reason(client.post('/attest', json=signed(issuer='issuer:mallory'))) == 'unknown_key'
    assert count(session_factory) == 0


def test_trust_file_reload_and_failure(client, signed, trust_data, tmp_path, monkeypatch, session_factory):
    app.dependency_overrides.pop(get_trust)
    monkeypatch.delenv('BITREP_TRUST_REGISTRY', raising=False)
    assert client.post('/attest', json=signed()).status_code == 503
    path = tmp_path / 'trust.json'
    monkeypatch.setenv('BITREP_TRUST_REGISTRY', str(path))
    assert client.post('/attest', json=signed()).status_code == 503
    path.write_text(json.dumps(trust_data))
    assert client.post('/attest', json=signed()).status_code == 201
    trust_data['keys'][0]['revoked_at'] = NOW
    path.write_text(json.dumps(trust_data))
    assert reason(client.post('/attest', json=signed())) == 'key_revoked'
    path.write_text('{bad')
    assert client.post('/verify', json=signed()).status_code == 503
    assert count(session_factory) == 1


@pytest.mark.parametrize('change', [{'valid_until': NOW}, {'published_at': NOW + 1}])
def test_stale_or_future_trust(client, signed, trust_data, session_factory, change):
    trust_data.update(change)
    assert client.post('/attest', json=signed()).status_code == 503
    assert count(session_factory) == 0


@pytest.mark.parametrize('mode', ['duplicate', 'bad_public_key', 'duplicate_json'])
def test_malformed_trust_snapshot(trust_data, tmp_path, monkeypatch, mode):
    if mode == 'duplicate': trust_data['keys'].append(trust_data['keys'][0])
    elif mode == 'bad_public_key': trust_data['keys'][0]['public_key'] = 'junk'
    raw = json.dumps(trust_data)
    if mode == 'duplicate_json': raw = raw.replace('"keys":', '"keys": [], "keys":')
    path = tmp_path / 'trust.json'; path.write_text(raw)
    monkeypatch.setenv('BITREP_TRUST_REGISTRY', str(path))
    with pytest.raises(TrustUnavailable): load_registry()


def test_portable_golden_vector(client):
    from pathlib import Path
    import hashlib
    from models.verification import AttestationEnvelope
    from utils.trust import TrustRegistry
    from utils.verification import verify_attestation
    fixture = json.loads(Path('tests/fixtures/verification-v1.json').read_text())
    att = AttestationEnvelope.model_validate(fixture['attestation'])
    assert canonical_bytes(att.statement) == fixture['canonical_ascii'].encode('ascii')
    assert att.statement.content_digest == 'sha256:' + hashlib.sha256(fixture['content_utf8'].encode()).hexdigest()
    assert verify_attestation(att, TrustRegistry.model_validate(fixture['trust']), fixture['evaluated_at']).model_dump() == fixture['verification']
    assert client.post('/verify', json=fixture['attestation']).json() == fixture['verification']
    # Wire formatting is not part of the signature.
    reordered = {'signature': att.signature, 'statement': dict(reversed(list(att.statement.model_dump().items())))}
    assert client.post('/verify', content=json.dumps(reordered, indent=4)).json() == fixture['verification']


def test_concurrent_duplicate_admission(tmp_path, trust_data, signed):
    """Real independent DB connections racing the same signed submission."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from fastapi import Response
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from db.connection import Base
    from api.attestations import create_attestation
    from models.verification import AttestationEnvelope
    from utils.trust import TrustRegistry
    engine = create_engine('sqlite:///' + str(tmp_path / 'race.db'), connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    barrier = Barrier(4)
    def submit(_):
        with factory() as db:
            barrier.wait()
            return create_attestation(Response(), AttestationEnvelope.model_validate(signed()), db,
                TrustRegistry.model_validate(trust_data), NOW)['admission']
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(submit, range(4)))
    assert sorted(results) == ['accepted', 'duplicate', 'duplicate', 'duplicate']
    assert count(factory) == 1
    engine.dispose()


def test_placeholder_does_not_mutate_legacy_flags(client, session_factory):
    with session_factory() as db:
        db.add(UserIdentityModel(username='alice', public_key='synthetic', private_key_hash='unused', verified=False))
        db.add(ThirdPartyAttestationModel(id=1, username='alice', platform='synthetic', attestation_type='asserts', verified=0))
        db.commit()
    assert client.post('/identity/alice/verify', json={'verified': True}).status_code == 501
    assert client.post('/integration/verify/1', json={'verified': True}).status_code == 501
    with session_factory() as db:
        assert db.query(UserIdentityModel).one().verified is False
        assert db.get(ThirdPartyAttestationModel, 1).verified == 0
