# Ticket 007: Bind immutable runtime rollout and supervisor isolation

- **ID**: ticket-007
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.4 with an exact-runtime rollout boundary derived from the
live failure where a systemd unit linked to a development checkout changed
before its pull request was merged. A conforming controller must execute from
an isolated protected revision, keep supervisor configuration outside the
development tree, quiesce triggers during rollout or rollback and prove the
new pin with a fresh automatic cycle.

## Acceptance criteria

- [x] AC-01: Require the runtime preflight to bind the exact deployed revision;
  membership in protected history alone is insufficient.
- [x] AC-02: Prohibit supervisor units and executable paths linked to candidate
  or concurrently mutable development workspaces.
- [x] AC-03: Require rollout and rollback to prepare and validate a replacement,
  quiesce triggers, reject dirty deployed state and switch the pin before
  effects resume.
- [x] AC-04: Record the zero-effect symlink incident, isolated recovery,
  autonomous exact-head merge and successful protected-runtime cycle.
- [x] AC-05: Promote exact artifacts to 0.4.0 and pass DSL, semantic, unit,
  self-test, compile, lint and governance checks.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication state

- Local semantic, DSL, unit, self-test, compile, lint and governance gates pass.
- Exact-head Validator App approval, protected merge, read-back and branch
  cleanup remain pending; the ticket stays `IN_PROGRESS / PUBLICATION`.
