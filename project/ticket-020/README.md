# Ticket 020: Autonomy continuation governance for subactor multi-agent operation

- **ID**: ticket-020
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Define and publish governance controls for autonomous continuation across multiple Subactor
agents in this repository: ticket ownership continuity, inter-workstream isolation, and
human-free continuation posture when evidence gates are satisfied.

This ticket updates only governance-owned files and records practical lessons from
`validator-agent` non-merge incidents and observed branch-handling constraints so future
autonomous runtime can continue without manual PR-by-PR decisions.

## Acceptance criteria

- [ ] AC-01: TODO includes an active governance entry for this ticket with clear
      continuation criteria and scope status.
- [ ] AC-02: `project/TICKETS.md` includes this ticket in the active ticket index and
      reflects governance ownership.
- [ ] AC-03: Root `README.md` captures the governance stance for multi-agent continuation
      and explicitly documents known edge-cases that do not increase autonomy authority.
- [ ] AC-04: `CHANGELOG.md` documents this governance alignment as an unreleased
      continuity standardization item.
- [ ] AC-05: No implementation/validation surface files (`spec`, `src`, `tests`,
      `profiles`, `examples`) are modified.
- [ ] AC-06: Required governance and conformance checks pass on the candidate.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
