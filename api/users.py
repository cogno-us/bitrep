"""List v1 admissions, with current re-verification and explicit historical results."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.attestations import get_db, get_trust, get_now, present_record
from models.attestation import AcceptedAttestationModel
from utils.trust import TrustRegistry

router = APIRouter()


@router.get('/user/{username}')
def get_user_attestations(username: str, db: Session = Depends(get_db),
                          trust: TrustRegistry = Depends(get_trust), now: int = Depends(get_now)) -> dict:
    rows = db.query(AcceptedAttestationModel).filter_by(subject=username).all()
    return {'user': username, 'attestations': [present_record(row, trust, now) for row in rows]}
