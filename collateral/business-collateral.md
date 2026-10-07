# BitRep — Business Collateral

## 1. Executive Summary

A binary-attestation protocol and reference verifier. The accepted v1 interface checks Ed25519 signatures against an operator-configured issuer-key trust snapshot and evaluation time. A successful result means issuer_signature_only under those conditions, not factual truth or institutional authority.

## 2. The Business Problem

An evidence consumer needs to know who signed a statement, which content it commits to and whether the key and statement are currently admissible. Unverified identity flags, copied verification JSON and legacy unsigned imports cannot supply that assurance.

## 3. The Component in One View

| Capability | Practical role |
|---|---|
| Strict signed statements | Bind version, algorithm, issuer/key, subject, type, audience, content digest and validity times. |
| Explicit trust snapshot | Require operator-controlled issuer keys and current snapshot validity; no default trusted issuer is supplied. |
| Current-state verification | Check signature, key status, audience and time constraints, including conservative revocation behavior. |
| Admission and duplicates | Keep accepted v1 records separate from legacy data; identical valid resubmission is idempotent and conflicting issuer/ID content is rejected. |
| Fail-closed assurance | Reject malformed or unsupported inputs and keep placeholder privacy/platform verification outside accepted assurance. |

## 4. Who Should Evaluate It

Engineers can inspect the reference contracts and examples; enterprise architecture, security and governance reviewers can examine the boundary and evidence. Evaluate this component for its named responsibility rather than as a complete governance platform.

## 5. A Bounded Workflow

A downstream system such as The Index supplies the expected subject, audience and content binding. BitRep verifies the signed statement locally or through the reference service under configured trust. The consumer still compares the digest with the exact bytes it uses and decides how much evidentiary weight to give the assertion. Two signed assertions about the same bytes are not automatically independent corroboration.

This is a reference use case. Adopting the format or running the example does not establish a production deployment, institutional acceptance or measured business benefit.

## 6. Relationship to the Stack

This component contributes **verify issuer signatures under explicit trust assumptions**. The [Cognous Open Control Stack](https://github.com/cogno-us/cognous-open-control-stack) connects declared proposals, independent authority, constrained execution and retained review evidence. Components remain separately owned and versioned; the [selected lock](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/component-lock.json) determines which revisions participate in the supported integration.

A valid signature, chain inclusion, message receipt, reasoning instruction or evidence-package digest does not authorize execution. Institutional authority must be supplied and evaluated through the appropriate trusted boundary.

## 7. What the Evidence Supports

The hub selects accepted v1 verifier `5b5077dafde232a7801cb425c4efddcffb468723` for the bounded evidence path. The [verification contract](../docs/VERIFICATION_CONTRACT_V1.md) retains its original proposal-stage header; current bounded adoption is evidenced by the hub lock and qualification. Its broader production and deployment decisions remain unresolved. Legacy RSA helpers and unsigned ingestion are not the v1 accepted path.

The [accepted hub evidence](https://github.com/cogno-us/cognous-open-control-stack/blob/5737267d94d2b445735c95e8480a31de73a2abe8/examples/control-plane-store-adoption/qualification-summary.json) supports bounded synthetic integration at its exact pins. Aggregate test totals do not establish deployment benefit, compliance or independent real-world verification. The [support ledger](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/release-status.md) distinguishes the standard reference, separate protected-worker campaign and unqualified production work.

## 8. What It Does Not Establish

No reputation score, real zero-knowledge proof, external-platform identity verification, blockchain inclusion verification, signed portable result receipt or caller-selected historical verification is established by v1. Issuer enrollment, secure time, snapshot distribution/anti-rollback and production transport authentication remain deployment work.

## 9. Evaluation Questions

- Which exact input, output and source revision will the receiving system consume?
- Who supplies trusted authority or evidence, and which assumptions remain outside this component?
- Can a reviewer trace the result to retained sources, including rejected or missing information?
- Which documented checks were actually executed in the intended environment?
- What deployment-specific work is required before relying on the result?

## 10. Why Open Reference Material Matters

Public formats, source, examples and evidence allow reviewers to inspect the claimed boundary and reproduce its checks. They also expose what has not been tested. Openness supports review; it does not substitute for independent assurance or operating responsibility.

## 11. Practical Next Step

Follow the [README](../README.md) and select one bounded use case. Inspect its inputs and expected outputs, reproduce the documented checks where prerequisites are available, and record failures and unresolved assumptions alongside passes. Use the [one-page overview](one-page-overview.md) for initial stakeholder orientation.

## 12. Status and Attribution

This collateral summarizes merged public material at repository `b820e6cf5a4be4c0cede5a6e80b20b6ef4aaf1e7` and the accepted hub baseline `5737267d94d2b445735c95e8480a31de73a2abe8`. It does not anticipate pending branches. The protected-worker result applies only to its recorded Linux/bubblewrap fixture; live OpenShell and logical-intent prevention are not hub-supported at this snapshot.

[Cognous](https://cogno.us) · [Source repository](https://github.com/cogno-us/cognous-evidence-attestation) · [Stack responsibilities](https://github.com/cogno-us/cognous-open-control-stack/blob/main/docs/architecture.md). Existing licenses and third-party notices remain controlling.
