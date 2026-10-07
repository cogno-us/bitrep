<!-- cognous-banner:start -->
```text
──────────────────────────────────────────────────
   __________  _______   ______  __  _______
  / ____/ __ \/ ____/ | / / __ \/ / / / ___/
 / /   / / / / / __/  |/ / / / / / / /\__ \
/ /___/ /_/ / /_/ / /|  / /_/ / /_/ /___/ /
\____/\____/\____/_/ |_/\____/\____//____/
               EVIDENCE ATTESTATION
       g o v e r n e d   b y   d e s i g n
  github.com/cogno-us/cognous-open-control-stack
──────────────────────────────────────────────────
```
<!-- cognous-banner:end -->

# BitRep

**Verify issuer signatures under explicit trust assumptions.**

## Overview

A binary-attestation protocol and reference verifier. The accepted v1 interface checks Ed25519 signatures against an operator-configured issuer-key trust snapshot and evaluation time. A successful result means issuer_signature_only under those conditions, not factual truth or institutional authority.

**Implementation status:** this README describes merged public reference work. Component acceptance, selection in the hub and execution of a qualification are separate facts. The selected revision for this component is `5b5077dafde232a7801cb425c4efddcffb468723`; the [hub lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) is the source of that integration choice.

## Purpose and intended users

An evidence consumer needs to know who signed a statement, which content it commits to and whether the key and statement are currently admissible. Unverified identity flags, copied verification JSON and legacy unsigned imports cannot supply that assurance.

Engineers can inspect the reference contracts and examples; enterprise architecture, security and governance reviewers can examine the boundary and evidence. Evaluate this component for its named responsibility rather than as a complete governance platform.

## Key features

| Capability | Implemented or specified responsibility |
|---|---|
| **Strict signed statements** | Bind version, algorithm, issuer/key, subject, type, audience, content digest and validity times. |
| **Explicit trust snapshot** | Require operator-controlled issuer keys and current snapshot validity; no default trusted issuer is supplied. |
| **Current-state verification** | Check signature, key status, audience and time constraints, including conservative revocation behavior. |
| **Admission and duplicates** | Keep accepted v1 records separate from legacy data; identical valid resubmission is idempotent and conflicting issuer/ID content is rejected. |
| **Fail-closed assurance** | Reject malformed or unsupported inputs and keep placeholder privacy/platform verification outside accepted assurance. |

## How it works

A downstream system such as The Index supplies the expected subject, audience and content binding. BitRep verifies the signed statement locally or through the reference service under configured trust. The consumer still compares the digest with the exact bytes it uses and decides how much evidentiary weight to give the assertion. Two signed assertions about the same bytes are not automatically independent corroboration.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## Getting started

From a fresh repository checkout, use Python 3.11+ and an activated virtual environment. Install only into that environment. Package installation needs network access; the commands below exercise local reference tooling. For the full selected integration, use the [hub quickstart](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/quickstart.md), whose runner supplies exact producer checkouts and test wiring.

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q tests/test_verification.py tests/test_api.py
```

These tests use synthetic fixtures. A service deployment additionally needs an operator-controlled `BITREP_TRUST_REGISTRY`, trusted time and appropriate access controls; test keys and copied verification JSON are not production credentials.

## Evidence and supported scope

The hub selects accepted v1 verifier `5b5077dafde232a7801cb425c4efddcffb468723` for the bounded evidence path. The [verification contract](docs/VERIFICATION_CONTRACT_V1.md) retains its original proposal-stage header; current bounded adoption is evidenced by the hub lock and qualification. Its broader production and deployment decisions remain unresolved. Legacy RSA helpers and unsigned ingestion are not the v1 accepted path.

The accepted [hub persistence-generation evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) records 915 Python tests in each of two repetitions, 35 matrix entries satisfying their gates and 120 separate mocked OpenShell tests. Those are aggregate hub results, not a per-component test count or a claim of production readiness. Optional behavioral layers receive static checks only. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) separates implementation, execution and adoption.

## Limitations and deployment decisions

No reputation score, real zero-knowledge proof, external-platform identity verification, blockchain inclusion verification, signed portable result receipt or caller-selected historical verification is established by v1. Issuer enrollment, secure time, snapshot distribution/anti-rollback and production transport authentication remain deployment work.

Review original artifacts and their exact source revisions before extending a claim to a new environment. New dependencies, authority sources, destinations or enforcement mechanisms need their own compatibility and qualification. A passing reference case is not a certification of an enterprise deployment.

## Repository guide

Use these sources for details; their historical checkpoints retain the status and scope of the work they recorded:

- [docs/VERIFICATION_CONTRACT_V1.md](docs/VERIFICATION_CONTRACT_V1.md)
- [tests/test_verification.py](tests/test_verification.py)
- [tests/test_api.py](tests/test_api.py)

For a nontechnical introduction, read the [business overview](collateral/business-collateral.md) and [one-page overview](collateral/one-page-overview.md). Both describe this component's role and evidence limits, not additional runtime features.

## Contributing and attribution

[Contribution guidance](CONTRIBUTING.md) describes review and validation expectations. Keep evidence-linked claims, preserve historical records and separate proposed features from accepted implementation.

See [LICENSE](LICENSE) and [attribution](NOTICE) for the existing terms and third-party scope. Developed by [Cognous](https://cogno.us); no licensing change is part of this documentation update.

---

## Bibliography

Selected external sources from the October 2026 research review. These inform evaluation questions; they do not establish Cognous implementation, adoption, conformance or production qualification.

- [OWASP GenAI Security Project. *State of Agentic AI Security and Governance*, version 2.01 (June 2026)](https://genai.owasp.org/resource/state-of-agentic-ai-security-and-governance/). Security synthesis covering agent identity, delegated permissions, tool access and containment.
- [Alexander Barrett. *Boundary Blindness Under Artificial Intelligence: Early Cross-Industry Findings on the Missing Decision-Evidence Layer* (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7210798). Working paper on carrying the basis for reliance across organizational boundaries; proposed architecture, not a validated interoperability guarantee.
- [Mick Yang et al. *AI Epistemic Risks: Emerging Mechanisms & Evidence* (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6873005). Research synthesis on persuasion, cognitive offloading and feedback loops; context for evidence quality and independent judgment.

See the [research bibliography](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/research-bibliography.md) for review scope and source-verification limits.

## Cognous stack components

[Stack hub](https://github.com/cogno-us/cognous-open-control-stack) · [Selected pins](https://github.com/cogno-us/cognous-open-control-stack/blob/main/component-lock.json) · [Evidence and limits](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md)

Component links are navigation, not a requirement to install every component. The hub lock determines its supported integration.

| Component | Responsibility |
|---|---|
| [Agent Action Manifest](https://github.com/cogno-us/cognous-action-manifest) | Declare the action before evaluating permission |
| [Agent Control Plane](https://github.com/cogno-us/cognous-control-plane) | Evaluate proposals against authority and preserve the decision record |
| [Agent Replay Bundle](https://github.com/cogno-us/cognous-replay-bundle) | Reconstruct what the retained records support |
| [Agent Governance Evidence Pack](https://github.com/cogno-us/cognous-governance-evidence-pack) | Turn traceable runtime records into reviewable governance evidence |
| [Open Decision Evidence Standard](https://github.com/cogno-us/open-decision-evidence-standard) | Portable decision evidence across system and organizational boundaries |
| [Alvorada Experimental Workbench](https://github.com/cogno-us/cognous-governed-exchange) | Governed exchange and continuity for a bounded synthetic workflow |
| [Moltbot Safe](https://github.com/cogno-us/cognous-execution-runtime) | Constrained execution beneath independent current authorization |
| [The Index](https://github.com/cogno-us/cognous-evidence-registry) | A local blockchain reference for claims, evidence commitments and lifecycle history |
| [Portable Reasoning Protocol v1.0](https://github.com/cogno-us/portable-reasoning-protocol) | Portable instructions for evidence-bounded reasoning |
| [Research Intelligence Protocol v1.0](https://github.com/cogno-us/research-intelligence-protocol) | Disciplined discovery and cross-domain abstraction, kept separate |
| [TFA Protocol (S43)](https://github.com/cogno-us/truth-freedom-agency-protocol) | Truth · Freedom · Agency |
| [Constitutional Governance for Institutions](https://github.com/cogno-us/cognous-institutional-governance) | Alvorada: authority, challenge and correction for institutions |

## Repository locations

See the [repository rename map and compatibility notes](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/repository-renames.md) for current component URLs. Existing package names, schema identifiers and retained producer identities are unchanged.
