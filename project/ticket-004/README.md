# Ticket 004: Bind live Autonomy 0.2 runtime evidence

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.2 from a static published contract to a practice-backed
standard after the `subactor/autonom` execution plane completed a fresh,
non-manual protected PR canary. Bind the normative queue/lease/checkpoint rules
to the failure windows discovered during deployment, and update the
Subactor/Semcod profile to the actual protected registry and runtime files.

## Acceptance criteria

- [x] AC-01: Record immutable live evidence for automatic trigger, exact
  five-field claim, registry digest, exact-head App approval, explicit App
  merge, merge SHA, branch deletion and durable checkpoint.
- [x] AC-02: Require a claim lease to outlive every bounded in-flight effect,
  durable state transitions to survive process/power interruption, and restart
  reconciliation to complete a committed checkpoint without replaying an
  unidentified effect.
- [x] AC-03: Require interrupted final receipts/canary indexes to be rebuilt
  from a complete protected checkpoint instead of losing proof or replaying
  publication.
- [x] AC-04: Update the Subactor/Semcod integration profile to name the actual
  queue, controller, timer and protected Validator registry contracts.
- [x] AC-05: Promote repository status to `0.2.0` and pass governance,
  conformance, self-test, compilation and lint checks.
- [x] AC-06: Keep the promoted manifest identity internally coherent by
  declaring both `status` and `lifecycle.stability` as `stable`, then pass the
  current shared DSL conformance checker.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
