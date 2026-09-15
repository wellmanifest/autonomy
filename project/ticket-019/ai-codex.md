---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-019
---
# Participant: codex (AI agent)

## Understanding

Autonomous mutation currently has branch-continuity requirements in core
standards, but unresolved non-default branches are not explicitly protected in an
operationally enforceable form for publish-stage policy. This leaves a practical
gap where branch cleanup can proceed without stable owner proof during parallel
agent execution.

## Execution plan

1. Update the canonical autonomy standard with deterministic branch continuity and
   orphan-handling semantics.
2. Bind these semantics into `profiles/subactor-semcod.profile.json` as explicit
   publish restrictions.
3. Add conformance assertions in `tests/test_autonomy.py` for both the standard
   text and profile restrictions.
4. Update dependent digest bindings in `examples/dsl-manifest.json` and
   `examples/valid/project.autonomy.json` so profile/standard artifact checks
   remain exact-byte true.

## Human-assistance extension

The Founder request on 2026-09-15 is recorded as
`SESSION_EXECUTION_AUTHORIZATION`. I will reuse this matching integration
ticket rather than allocate a competing integration ticket. The extension
formalizes a typed `human-assistance/v1` request and response, exact subject
and digest bindings, expiry, and an effect-frozen waiting state. It remains
advisory until a protected adapter authenticates the actor; LLM output cannot
be consent.

## Actual changes

- Added branch-continuity/orphan-handling requirements to
  `spec/AUTONOMY_STANDARD.md`.
- Added publish restrictions
  `orphan-branch-preservation-policy` and
  `provider-branch-inventory-authority` to
  `profiles/subactor-semcod.profile.json`.
- Added assertions for those restrictions and related normative phrases in
  `tests/test_autonomy.py`.
- Confirmed evidence updates for this implementation were limited to this
  ticket's scope.
- Added SC-009..SC-012 requirements to the supervisor continuation profile.
- Added pure request/response and waiting-state checks to
  `src/continuation_check.py`, with CLI kinds `human-request` and
  `human-response`.
- Added protocol documentation, Subactor dispatch/publish restrictions and
  conformance tests.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access,
  external coordination, material objective expansion, and trusted merge
  approval.
