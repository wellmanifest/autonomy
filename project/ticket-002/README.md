# Ticket 002: Standardize reliable autonomous execution from operational evidence

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Revise the experimental Autonomy standard from observed production behavior.
The contract must preserve no-per-PR-human autonomy while refusing to confuse
a successful manual dispatch with scheduler liveness, a green target with a
green aggregate matrix, or platform-native auto-merge with protected explicit
Validator App publication.

## Acceptance criteria

- [ ] AC-01: The normative standard distinguishes execution correctness,
  trigger liveness and end-to-end operational proof.
- [ ] AC-02: The v2 manifest requires a durable at-least-once queue,
  checkpoints, exact idempotency bindings and bounded dead-letter behavior.
- [ ] AC-03: A protected primary trigger and independent watchdog recover from
  missed scheduler delivery without requiring per-PR human action.
- [ ] AC-04: Manual dispatch is diagnostic only and cannot satisfy scheduler
  or canary liveness conformance.
- [ ] AC-05: Validation and publication outcomes are isolated per repository;
  unrelated matrix failures cannot invalidate or block a passing target.
- [ ] AC-06: One protected registry owns repository/base/check/validator/merge
  bindings and conformance rejects duplicated-profile drift.
- [ ] AC-07: Publication requires explicit protected App merge while native
  platform auto-merge remains disabled.
- [ ] AC-08: A fresh protected low-risk canary proves trigger, claim,
  exact-head validation, merge, readback and branch cleanup receipts.
- [ ] AC-09: The Subactor/Semcod profile maps dispatch, watchdog and durable
  queue ownership without moving runtime code into Wellmanifest.
- [ ] AC-10: Schema, examples, checker and regression tests reject single-cron,
  global-fail-fast, stale-canary and native-auto-merge configurations.
- [ ] AC-11: Governance, unit, semantic, DSL, compilation and lint checks pass.
- [ ] AC-12: The current standard is published through protected exact-head
  review and App-owned merge, closing the historical publication gap.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
