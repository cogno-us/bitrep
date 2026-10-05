"""Demonstration proofs are unavailable to HTTP assurance consumers."""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post('/privacy/prove-threshold')
@router.post('/privacy/verify-threshold')
@router.post('/privacy/selective-disclosure')
def privacy_not_implemented() -> None:
    raise HTTPException(501, detail={
        'reason': 'demonstration_only', 'assurance': 'none',
        'message': 'No proposition-verifying privacy proof system is implemented.',
    })
