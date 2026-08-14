# Ticket 015: Repair Autonomy DSL artifact digest closure

- **ID**: ticket-015
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Repair the stale artifact digests published in the Autonomy 0.7 DSL manifest
and issue a semver patch release. Keep the v5 semantics unchanged while
advancing the release/profile binding to 0.7.1 and proving the external DSL
checker against every exact artifact byte.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes the repair from exact
      protected `main@ff11f595`.
- [ ] AC-02: VERSION, DSL manifest, profile selection and version assertion
      advance coherently to 0.7.1 without a schema-generation change.
- [ ] AC-03: Every DSL artifact digest equals the exact published candidate
      byte content; no stale digest remains.
- [ ] AC-04: The Autonomy checker, JSON Schema validator and external
      Wellmanifest DSL checker all pass.
- [ ] AC-05: Only the five declared implementation files and ticket governance
      paths change; root release docs remain a separate governance workstream.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
