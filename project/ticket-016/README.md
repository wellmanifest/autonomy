# Ticket 016: Align root docs with Autonomy 0.7.1

- **ID**: ticket-016
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Align the governance-owned root landing page and changelog with the already
published stable Autonomy 0.7.1 patch. Record the exact digest repair and its
protected publication, including the distinction between successful recovery
execution and an undelivered scheduled heartbeat, without changing normative,
executable or integration artifacts.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes this documentation-only
      update from exact protected `main@79df4acc`.
- [ ] AC-02: README identifies stable 0.7.1 and records exact-byte DSL digest
      closure without changing the Autonomy 0.7 semantic contract.
- [ ] AC-03: README distinguishes the missed scheduled heartbeat from the
      successful protected matrix direct-scan recovery.
- [ ] AC-04: CHANGELOG records Autonomy 0.7.1 and exact publication evidence;
      only two implementation files change and every deterministic gate passes.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
