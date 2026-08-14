# Ticket 005: Standardize protected runtime source isolation

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.3 with a deployment-source integrity boundary derived from
the live incident where a shared Validator development checkout changed
registry bytes. The execution plane must use isolated protected revisions and
an external preflight, preserve concurrent work, and make zero mutations on
source or policy drift.

## Acceptance criteria

- [ ] AC-01: Require runtime executables, effect-capable dependencies and
  authority inputs to resolve from isolated, revision/digest-bound deployment
  artifacts rather than candidate or concurrent development workspaces.
- [ ] AC-02: Require a supervisor outside the loaded controller code to reject
  dirty deployment state or a revision outside the protected deployment ref.
- [ ] AC-03: Require zero external mutations and a degraded receipt when source
  or policy preflight fails, while preserving concurrent developer state.
- [ ] AC-04: Bind the Subactor profile and architecture evidence to the deployed
  systemd preflight, detached registry worktree and protected recovery run.
- [ ] AC-05: Promote exact artifacts to 0.3.0 and pass DSL, semantic, unit,
  self-test, compile, lint and governance checks.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
