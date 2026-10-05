# Legacy RSA helpers: NOT the v1 admission/signing contract. See utils/verification.py.
# Cryptographic utilities for identity and attestation signing

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import hashlib
import json
from typing import Tuple

def generate_keypair() -> Tuple[str, str]:
    """
    Generate RSA public/private key pair
    Returns: (public_key_pem, private_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return public_pem, private_pem

def sign_attestation(attestation_data: dict, private_key_pem: str) -> str:
    """
    Sign attestation data with private key
    Returns: Base64 encoded signature
    """
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )
    
    message = json.dumps(attestation_data, sort_keys=True).encode('utf-8')
    
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    import base64
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(attestation_data: dict, signature: str, public_key_pem: str) -> bool:
    """
    Verify attestation signature with public key
    Returns: True if signature is valid
    """
    try:
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        message = json.dumps(attestation_data, sort_keys=True).encode('utf-8')
        
        import base64
        signature_bytes = base64.b64decode(signature)
        
        public_key.verify(
            signature_bytes,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def hash_private_key(private_key_pem: str) -> str:
    """
    Hash private key for storage (never store actual private key)
    """
    return hashlib.sha256(private_key_pem.encode('utf-8')).hexdigest()
