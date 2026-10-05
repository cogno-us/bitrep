# Tests for zero-knowledge proof utilities

import pytest
from utils.zkproof import (
    generate_zk_proof,
    verify_zk_proof,
    create_selective_disclosure_proof,
    verify_selective_disclosure
)

def test_generate_zk_proof_meets_threshold():
    """Test ZK proof generation when attestation count meets threshold."""
    attestation_count = 10
    threshold = 5
    
    proof, meets_threshold = generate_zk_proof(attestation_count, threshold)
    
    assert proof is not None
    assert len(proof) == 64  # SHA256 hex digest
    assert meets_threshold is True

def test_generate_zk_proof_fails_threshold():
    """Test ZK proof generation when attestation count doesn't meet threshold."""
    attestation_count = 3
    threshold = 5
    
    proof, meets_threshold = generate_zk_proof(attestation_count, threshold)
    
    assert proof is not None
    assert meets_threshold is False

def test_verify_zk_proof_valid():
    """Even generated demonstration hashes cannot establish assurance."""
    attestation_count = 10
    threshold = 5
    
    proof, meets_threshold = generate_zk_proof(attestation_count, threshold)
    is_valid = verify_zk_proof(proof, threshold, meets_threshold)
    
    assert is_valid is False

def test_verify_zk_proof_invalid_format():
    """Test verification fails for invalid proof format."""
    invalid_proof = "not_a_valid_proof"
    threshold = 5
    
    is_valid = verify_zk_proof(invalid_proof, threshold, True)
    assert is_valid is False

def test_create_selective_disclosure_proof():
    """Test creation of selective disclosure proof."""
    attestations = [
        {"id": 1, "issuer": "alice", "attestation_type": "peer_verified"},
        {"id": 2, "issuer": "bob", "attestation_type": "peer_verified"},
        {"id": 3, "issuer": "charlie", "attestation_type": "peer_verified"},
    ]
    selected_indices = [0, 2]  # Disclose first and third
    
    proof = create_selective_disclosure_proof(attestations, selected_indices)
    
    assert "merkle_root" in proof
    assert proof["total_count"] == 3
    assert len(proof["disclosed_attestations"]) == 2
    assert proof["disclosed_attestations"][0]["id"] == 1
    assert proof["disclosed_attestations"][1]["id"] == 3

def test_verify_selective_disclosure():
    """Generated selective-disclosure demonstrations fail assurance verification."""
    attestations = [
        {"id": 1, "issuer": "alice", "attestation_type": "peer_verified"},
        {"id": 2, "issuer": "bob", "attestation_type": "peer_verified"},
    ]
    selected_indices = [0]
    
    proof = create_selective_disclosure_proof(attestations, selected_indices)
    is_valid = verify_selective_disclosure(proof, proof["disclosed_attestations"])
    
    assert is_valid is False

def test_verify_selective_disclosure_invalid():
    """Test verification fails for mismatched disclosure."""
    attestations = [
        {"id": 1, "issuer": "alice", "attestation_type": "peer_verified"},
    ]
    selected_indices = [0]
    
    proof = create_selective_disclosure_proof(attestations, selected_indices)
    
    # Try to verify with wrong attestations
    wrong_attestations = [
        {"id": 2, "issuer": "bob", "attestation_type": "peer_verified"},
    ]
    
    is_valid = verify_selective_disclosure(proof, wrong_attestations)
    assert is_valid is False  # Demonstrations never establish assurance
