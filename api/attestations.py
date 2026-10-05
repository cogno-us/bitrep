"""Fail-closed v1 verification and admission boundary."""
import json
import time
from typing import Iterator
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db.connection import SessionLocal
from models.attestation import AcceptedAttestationModel
from models.verification import AttestationEnvelope, VerificationResult
from utils.trust import load_registry, strict_json, TrustRegistry, TrustUnavailable
from utils.verification import verify_attestation

router = APIRouter()


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_now() -> int:
    return int(time.time())


def get_trust() -> TrustRegistry:
    try:
        return load_registry()
    except TrustUnavailable as exc:
        raise HTTPException(503, detail={'reason': 'trust_unavailable'}) from exc


async def parse_attestation(request: Request) -> AttestationEnvelope:
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 16384:
            raise HTTPException(413, detail={'reason': 'input_too_large'})
    try:
        return AttestationEnvelope.model_validate(strict_json(bytes(raw)))
    except (ValueError, ValidationError) as exc:
        raise HTTPException(422, detail={'reason': 'malformed_input'}) from exc


def evaluate(att: AttestationEnvelope, trust: TrustRegistry, now: int) -> VerificationResult:
    try:
        return verify_attestation(att, trust, now)
    except TrustUnavailable as exc:
        raise HTTPException(503, detail={'reason': 'trust_unavailable'}) from exc


@router.post('/verify', response_model=VerificationResult)
def verify(att: AttestationEnvelope = Depends(parse_attestation),
           trust: TrustRegistry = Depends(get_trust), now: int = Depends(get_now)) -> VerificationResult:
    return evaluate(att, trust, now)


@router.post('/attest')
def create_attestation(response: Response, att: AttestationEnvelope = Depends(parse_attestation),
                       db: Session = Depends(get_db), trust: TrustRegistry = Depends(get_trust),
                       now: int = Depends(get_now)) -> dict:
    result = evaluate(att, trust, now)
    if result.outcome != 'verified':
        raise HTTPException(422, detail=result.model_dump())
    statement = att.statement

    def find_existing() -> AcceptedAttestationModel | None:
        return db.query(AcceptedAttestationModel).filter_by(
            issuer=statement.issuer, attestation_id=statement.attestation_id
        ).first()

    def duplicate(existing: AcceptedAttestationModel) -> dict:
        if existing.statement_digest != result.statement_digest:
            raise HTTPException(409, detail={'reason': 'attestation_id_conflict'})
        return {'admission': 'duplicate', 'accepted_at': existing.accepted_at,
                'verification': result.model_dump()}

    existing = find_existing()
    if existing is not None:
        return duplicate(existing)
    row = AcceptedAttestationModel(
        statement_digest=result.statement_digest, issuer=statement.issuer,
        attestation_id=statement.attestation_id, subject=statement.subject,
        envelope_json=att.model_dump_json(), verification_json=result.model_dump_json(),
        accepted_at=now,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Database uniqueness is the race barrier across workers/processes.
        db.rollback()
        existing = find_existing()
        if existing is None:
            raise
        return duplicate(existing)
    response.status_code = 201
    return {'admission': 'accepted', 'accepted_at': now, 'verification': result.model_dump()}


def present_record(row: AcceptedAttestationModel, trust: TrustRegistry, now: int) -> dict:
    att = AttestationEnvelope.model_validate_json(row.envelope_json)
    return {'attestation': att.model_dump(), 'accepted_at': row.accepted_at,
            'verification_at_acceptance': json.loads(row.verification_json),
            'verification': evaluate(att, trust, now).model_dump()}


@router.get('/attestations/{digest}')
def get_attestation(digest: str, db: Session = Depends(get_db),
                    trust: TrustRegistry = Depends(get_trust), now: int = Depends(get_now)) -> dict:
    row = db.get(AcceptedAttestationModel, digest)
    if row is None:
        raise HTTPException(404, detail={'reason': 'not_found'})
    return present_record(row, trust, now)
