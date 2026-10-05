# API endpoints for identity management

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.connection import SessionLocal
from models.identity import UserIdentityModel
from models.user import UserIdentity, UserIdentityCreate
from utils.crypto import generate_keypair, hash_private_key
from typing import Dict

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/identity/create", response_model=Dict)
def create_identity(user_data: UserIdentityCreate, db: Session = Depends(get_db)):
    """
    Create a new identity with cryptographic key pair.
    Returns public key and private key (store private key securely on client side).
    """
    # Check if username already exists
    existing = db.query(UserIdentityModel).filter(
        UserIdentityModel.username == user_data.username
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Generate key pair
    public_key, private_key = generate_keypair()
    
    # Create identity
    identity = UserIdentityModel(
        username=user_data.username,
        public_key=public_key,
        private_key_hash=hash_private_key(private_key),
        verified=False
    )
    
    db.add(identity)
    db.commit()
    db.refresh(identity)
    
    return {
        "username": identity.username,
        "public_key": identity.public_key,
        "private_key": private_key,  # Return once, client must store securely
        "message": "Store your private key securely. It cannot be recovered."
    }

@router.get("/identity/{username}", response_model=UserIdentity)
def get_identity(username: str, db: Session = Depends(get_db)):
    """
    Get user identity information (public data only).
    """
    identity = db.query(UserIdentityModel).filter(
        UserIdentityModel.username == username
    ).first()
    
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    return UserIdentity(
        username=identity.username,
        public_key=identity.public_key,
        verified=identity.verified
    )

@router.post("/identity/{username}/verify")
def verify_identity(username: str, verification_data: Dict, db: Session = Depends(get_db)):
    """External identity verification is not implemented and cannot enroll trusted keys."""
    raise HTTPException(501, detail={"reason": "identity_verification_not_implemented"})
