# Integration tests for API endpoints

import pytest
from fastapi.testclient import TestClient
from main import app
import json



def test_root_endpoint(client):
    """Test that server is running."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_create_identity(client):
    """Test identity creation endpoint."""
    response = client.post(
        "/identity/create",
        json={"username": "test_user_1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert "private_key" in data
    assert data["username"] == "test_user_1"

def test_create_duplicate_identity(client):
    """Test that duplicate username is rejected."""
    client.post("/identity/create", json={"username": "test_user_2"})
    
    # Try to create again
    response = client.post(
        "/identity/create",
        json={"username": "test_user_2"}
    )
    assert response.status_code == 400

def test_get_identity(client):
    """Test getting identity information."""
    # Create identity first
    create_response = client.post(
        "/identity/create",
        json={"username": "test_user_3"}
    )
    
    # Get identity
    response = client.get("/identity/test_user_3")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user_3"
    assert "public_key" in data
    assert "reputation_score" not in data

def test_create_attestation(client, signed):
    response = client.post('/attest', json=signed())
    assert response.status_code == 201
    assert response.json()['verification']['outcome'] == 'verified'
    assert 'weight' not in response.json()


def test_get_user_attestations(client, signed):
    for n in range(2):
        assert client.post('/attest', json=signed(attestation_id=f'test-{n}')).status_code == 201
    response = client.get('/user/claim:42')
    assert response.status_code == 200
    assert len(response.json()['attestations']) == 2
    assert 'reputation' not in response.json()


def test_create_governance_proposal(client):
    """Test creating a governance proposal."""
    # Create identity first
    client.post("/identity/create", json={"username": "proposer_1"})
    
    response = client.post(
        "/governance/proposal",
        json={
            "title": "Test Proposal",
            "description": "A test governance proposal",
            "proposer": "proposer_1",
            "days_until_expiry": 7
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Proposal"
    assert data["status"] == "active"

def test_list_governance_proposals(client):
    """Test listing governance proposals."""
    response = client.get("/governance/proposals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_prove_attestation_threshold(client):
    response = client.post('/privacy/prove-threshold', json={'username': 'test', 'threshold': 5})
    assert response.status_code == 501
    assert response.json()['detail']['assurance'] == 'none'


def test_list_supported_platforms(client):
    """Test listing supported third-party platforms."""
    response = client.get("/integration/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "supported_platforms" in data
    assert "github" in data["supported_platforms"]
    assert "ebay" in data["supported_platforms"]

def test_import_third_party_attestation(client):
    """Test importing third-party attestation."""
    # Create identity first
    client.post("/identity/create", json={"username": "import_test_user"})
    
    response = client.post(
        "/integration/import",
        json={
            "username": "import_test_user",
            "platform": "github",
            "platform_username": "githubuser",
            "attestation_type": "commits",
            "value": 50.0,
            "metadata": {"repo_count": 10}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "github"
    assert data["verified"] == 0  # Pending verification
    assert "weight" not in data
