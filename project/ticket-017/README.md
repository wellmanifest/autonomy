# Ticket 017: Standardize heartbeat correlation and idempotent effects

- **ID**: ticket-017
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Turn the production evidence from Autonomy 0.7.1 publication into enforceable
Autonomy 0.8 contracts. A conforming project must expose scheduler heartbeat
freshness independently from recovery, select only the exact post-dispatch run
bound to its correlation identity, and reconcile repeated effects to one
authoritative external receipt without issuing a second review or merge.

## Acceptance criteria

- [ ] AC-01: The user's continuation request authorizes implementation from
      exact protected `main@0f5f80ab` without a second per-PR confirmation.
- [ ] AC-02: Manifest v6 requires a scheduler heartbeat SLO, protected
      missed-cycle monitoring and explicit late-delivery deduplication; manual
      recovery cannot be counted as scheduler-liveness evidence.
- [ ] AC-03: Manifest v6 requires pre-dispatch observation boundaries and
      exact repository, target, head, strategy and correlation bindings for
      both direct and matrix child run selection.
- [ ] AC-04: Manifest v6 requires at most one authoritative external effect;
      an `already-applied` outcome is valid only after exact external
      read-back, while stale, ambiguous and closed-unmerged subjects fail
      closed.
- [ ] AC-05: The Subactor/Semcod profile, valid and invalid examples,
      architecture and logic flow encode the observed missed heartbeat,
      bounded recovery and duplicate no-op publication evidence precisely.
- [ ] AC-06: Governance, semantic, schema, unit, compile, lint and external
      DSL validation pass with exact artifact digests and no new runtime
      dependency.
- [ ] AC-07: Publication occurs only through independent exact-head Validator
      App review, explicit protected merge, read-back and branch cleanup.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
