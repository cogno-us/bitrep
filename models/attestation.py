# attestation model

from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from datetime import datetime
from db.connection import Base

class AttestationModel(Base):
    __tablename__ = "attestations"

    id = Column(Integer, primary_key=True, index=True)
    issuer = Column(String, index=True)
    subject = Column(String, index=True)
    attestation_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    signature = Column(Text)
    anchor = Column(String)


class AcceptedAttestationModel(Base):
    """Only v1 verified admissions; legacy rows are never automatically promoted."""
    __tablename__ = 'accepted_attestations_v1'
    __table_args__ = (UniqueConstraint('issuer', 'attestation_id', name='uq_v1_issuer_id'),)

    statement_digest = Column(String, primary_key=True)
    issuer = Column(String, nullable=False)
    attestation_id = Column(String, nullable=False)
    subject = Column(String, nullable=False, index=True)
    envelope_json = Column(Text, nullable=False)
    verification_json = Column(Text, nullable=False)
    accepted_at = Column(Integer, nullable=False)
