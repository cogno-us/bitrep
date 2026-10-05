from fastapi import FastAPI
from db.connection import Base, engine
from api.attestations import router as attest_router
from api.users import router as users_router
from api.identity import router as identity_router
from api.governance import router as governance_router
from api.privacy import router as privacy_router
from api.integration import router as integration_router
from models.attestation import AttestationModel
from models.identity import UserIdentityModel
from models.governance import GovernanceProposalModel, VoteModel
from models.third_party import ThirdPartyAttestationModel

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BitRep Attestations - Modular", debug=False)

app.include_router(attest_router)
app.include_router(users_router)
app.include_router(identity_router)
app.include_router(governance_router)
app.include_router(privacy_router)
app.include_router(integration_router)
