# Ticket 005: Standardize protected runtime source isolation

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.3 with a deployment-source integrity boundary derived from
the live incident where a shared Validator development checkout changed
registry bytes. The execution plane must use isolated protected revisions and
an external preflight, preserve concurrent work, and make zero mutations on
source or policy drift.

## Acceptance criteria

- [x] AC-01: Require runtime executables, effect-capable dependencies and
  authority inputs to resolve from isolated, revision/digest-bound deployment
  artifacts rather than candidate or concurrent development workspaces.
- [x] AC-02: Require a supervisor outside the loaded controller code to reject
  dirty deployment state or a revision outside the protected deployment ref.
- [x] AC-03: Require zero external mutations and a degraded receipt when source
  or policy preflight fails, while preserving concurrent developer state.
- [x] AC-04: Bind the Subactor profile and architecture evidence to the deployed
  systemd preflight, detached registry worktree and protected recovery run.
- [x] AC-05: Promote exact artifacts to 0.3.0 and pass DSL, semantic, unit,
  self-test, compile, lint and governance checks.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted governance and Autonomy conformance checks passed on exact head
  `51781b04a887559411cfae955eb8d4a0344a3f42`.
- Validator run `31828176479` completed successfully and App review
  `4940097631` approved that exact head.
- The Validator App explicitly merged PR #8 as
  `d45d0d2aa31af45a23ea712e9a6be9e99a01b087`.
- Protected `main` read-back returned the same merge commit and the source
  branch was deleted.
- This publication was directly dispatched after ticket-004 had independently
  proved scheduled liveness; it is publication evidence, not another canary.
