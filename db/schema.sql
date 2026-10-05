-- BitRep database schema (binary-attestation model)

CREATE TABLE IF NOT EXISTS user_identities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    public_key TEXT UNIQUE NOT NULL,
    private_key_hash TEXT NOT NULL,
    verified INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attestations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issuer TEXT NOT NULL,
    subject TEXT NOT NULL,
    attestation_type TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    signature TEXT,
    anchor TEXT
);

CREATE TABLE IF NOT EXISTS governance_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    proposer TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    votes_for REAL DEFAULT 0.0,
    votes_against REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id INTEGER NOT NULL,
    voter TEXT NOT NULL,
    vote_value REAL NOT NULL,
    support INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS third_party_attestations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    platform TEXT NOT NULL,
    platform_username TEXT,
    attestation_type TEXT NOT NULL,
    value REAL,
    attestation_metadata TEXT,
    verified INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- v1 admissions are isolated from legacy attestations; never bulk-promote old rows.
CREATE TABLE IF NOT EXISTS accepted_attestations_v1 (
    statement_digest TEXT PRIMARY KEY NOT NULL,
    issuer TEXT NOT NULL,
    attestation_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    verification_json TEXT NOT NULL,
    accepted_at INTEGER NOT NULL,
    CONSTRAINT uq_v1_issuer_id UNIQUE (issuer, attestation_id)
);
CREATE INDEX IF NOT EXISTS ix_accepted_attestations_v1_subject
    ON accepted_attestations_v1 (subject);
