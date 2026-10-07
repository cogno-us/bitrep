# Cognous Evidence Attestation — One-Page Overview

## Purpose

A binary-attestation protocol and reference verifier. The accepted v1 interface checks Ed25519 signatures against an operator-configured issuer-key trust snapshot and evaluation time. A successful result means issuer_signature_only under those conditions, not factual truth or institutional authority.

## Problem

An evidence consumer needs to know who signed a statement, which content it commits to and whether the key and statement are currently admissible. Unverified identity flags, copied verification JSON and legacy unsigned imports cannot supply that assurance.

## What It Provides

- **Strict signed statements:** Bind version, algorithm, issuer/key, subject, type, audience, content digest and validity times.
- **Explicit trust snapshot:** Require operator-controlled issuer keys and current snapshot validity; no default trusted issuer is supplied.
- **Current-state verification:** Check signature, key status, audience and time constraints, including conservative revocation behavior.
- **Admission and duplicates:** Keep accepted v1 records separate from legacy data; identical valid resubmission is idempotent and conflicting issuer/ID content is rejected.

## Where It Fits

A downstream system such as Cognous Evidence Registry supplies the expected subject, audience and content binding. Cognous Evidence Attestation verifies the signed statement locally or through the reference service under configured trust. The consumer still compares the digest with the exact bytes it uses and decides how much evidentiary weight to give the assertion. Two signed assertions about the same bytes are not automatically independent corroboration.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Evidence and Limits

The [accepted hub lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) selects this component at `5b5077dafde232a7801cb425c4efddcffb468723`. Read the component's [README](../README.md) for version-specific acceptance and the [hub support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) for the executed scope. Component acceptance is not automatic adoption of newer revisions or production qualification.

No reputation score, real zero-knowledge proof, external-platform identity verification, blockchain inclusion verification, signed portable result receipt or caller-selected historical verification is established by v1. Issuer enrollment, secure time, snapshot distribution/anti-rollback and production transport authentication remain deployment work.

## Practical Next Step

Choose one bounded example and follow the [README](../README.md). Compare expected and observed results and retain uncertainty. The [business collateral](business-collateral.md) supplies evaluation questions and the component's wider context.

[Cognous](https://cogno.us) · [Source](https://github.com/cogno-us/cognous-evidence-attestation) · [All stack components](https://github.com/cogno-us/cognous-open-control-stack). Existing licenses and notices apply.
