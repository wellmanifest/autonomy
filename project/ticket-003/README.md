# Ticket 003: Onboard protected autonomy conformance

- **ID**: ticket-003
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Add a deterministic hosted check for the Autonomy standard so branch rules and
the independent Validator App can bind publication to the exact tested head.
This ticket owns CI onboarding only; normative Autonomy 0.2 content remains in
ticket-002.

## Acceptance criteria

- [x] AC-01: `standards / autonomy conformance` runs unit tests, the checker
  self-test and bytecode compilation for pull requests and `main`.
- [x] AC-02: Local governance and deterministic conformance checks pass.
- [ ] AC-03: An active ruleset requires current-head governance, conformance
  and one approval from someone other than the last pusher.
- [ ] AC-04: The Validator App is onboarded with the same exact required-check
  tuple used by direct validation and scheduled scan paths.
- [ ] AC-05: The workflow is merged without native auto-merge and is readable
  from `main` before Autonomy 0.2 publication proceeds.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
