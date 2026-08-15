# Ticket 018: Align root documentation with Autonomy 0.8

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Align the governance-owned root landing page and changelog with the already
published stable Autonomy 0.8 standard. Explain its scheduler-heartbeat,
correlation-bound run selection and idempotent effect-reconciliation contracts,
and bind the release summary to the exact protected publication receipts
without changing normative, executable or integration artifacts.

## Acceptance criteria

- [ ] AC-01: The user's continuation request authorizes this documentation-only
      update from exact protected `main@85eea5f0`.
- [ ] AC-02: README identifies stable 0.8.0 / manifest v6 and accurately
      summarizes heartbeat, correlation and effect-reconciliation boundaries.
- [ ] AC-03: README preserves the distinction between recovery execution and
      scheduler liveness and records exact practice/publication evidence.
- [ ] AC-04: CHANGELOG records the 0.8 contract, exact profile/DSL bindings and
      protected Validator publication plus governance closure.
- [ ] AC-05: Only README and CHANGELOG change as implementation files and all
      deterministic, schema and external DSL gates pass.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
