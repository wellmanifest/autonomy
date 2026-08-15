# Ticket 018: Align root documentation with Autonomy 0.8

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-15

## Goal and scope

Align the governance-owned root landing page and changelog with the already
published stable Autonomy 0.8 standard. Explain its scheduler-heartbeat,
correlation-bound run selection and idempotent effect-reconciliation contracts,
and bind the release summary to the exact protected publication receipts
without changing normative, executable or integration artifacts.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes this documentation-only
      update from exact protected `main@85eea5f0`.
- [x] AC-02: README identifies stable 0.8.0 / manifest v6 and accurately
      summarizes heartbeat, correlation and effect-reconciliation boundaries.
- [x] AC-03: README preserves the distinction between recovery execution and
      scheduler liveness and records exact practice/publication evidence.
- [x] AC-04: CHANGELOG records the 0.8 contract, exact profile/DSL bindings and
      protected Validator publication plus governance closure.
- [x] AC-05: Only README and CHANGELOG change as implementation files and all
      deterministic, schema and external DSL gates pass.
- [x] AC-06: The documentation candidate is published only through independent
      exact-head Validator App review, protected merge and branch cleanup.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted autonomy conformance run `31856627266` and remote lifecycle run
  `31856627257` passed on exact head
  `9fd3d9bbeeb9fa78d27c27433ef51d1b2bc0691b`.
- The helper bounded run selection above `31856383207` and selected Validator
  run `31856647275` with correlation
  `autonomy-pr-34-ticket-018-root-9fd3d9bbee`.
- Validator App review `4942337032` approved that exact head and protected
  policy converged after two stable reads.
- The Validator App explicitly merged PR #34 as
  `3e15a442a07ade17d6d42bd4fc2434aaac6db484`; protected `main` returned the
  same SHA and the source branch was absent.
