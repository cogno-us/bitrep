"""Isolated database per test; no tests write application storage."""
import base64
import copy
import hashlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from db.connection import Base
from main import app
from api import attestations, identity, governance, integration
from models.verification import SignedStatement
from utils.trust import TrustRegistry
from utils.verification import canonical_bytes

NOW = 1800000000


@pytest.fixture
def session_factory():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


@pytest.fixture
def signing_key():
    # Public synthetic test seed, never deploy this key.
    return Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


@pytest.fixture
def trust_data(signing_key):
    public = signing_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return {'registry_version': 'bitrep-trust/1', 'audience': 'index:test',
            'published_at': NOW - 100, 'valid_until': NOW + 1000,
            'keys': [{'issuer': 'issuer:alice', 'key_id': 'key:1',
                      'public_key': base64.b64encode(public).decode(),
                      'valid_from': NOW - 100, 'valid_until': NOW + 1000, 'revoked_at': None}]}


@pytest.fixture
def signed(signing_key):
    def make(**changes):
        data = {'protocol_version': 'bitrep-attestation/1', 'algorithm': 'Ed25519',
                'attestation_id': 'test-001', 'issuer': 'issuer:alice', 'key_id': 'key:1',
                'subject': 'claim:42', 'statement_type': 'asserts', 'audience': 'index:test',
                'content_digest': 'sha256:' + hashlib.sha256(b'synthetic evidence').hexdigest(),
                'issued_at': NOW - 10, 'not_before': NOW - 10, 'expires_at': NOW + 100}
        data.update(changes)
        statement = SignedStatement.model_validate(data)
        return {'statement': data, 'signature': base64.b64encode(signing_key.sign(canonical_bytes(statement))).decode()}
    return make


@pytest.fixture
def client(session_factory, trust_data):
    def get_db():
        with session_factory() as db:
            yield db
    for module in (attestations, identity, governance, integration):
        app.dependency_overrides[module.get_db] = get_db
    app.dependency_overrides[attestations.get_trust] = lambda: TrustRegistry.model_validate(copy.deepcopy(trust_data))
    app.dependency_overrides[attestations.get_now] = lambda: NOW
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
