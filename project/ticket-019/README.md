# Ticket 019: Strengthen orphan-branch and practice-based convergence standards

- **ID**: ticket-019
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Align the repository's normative standard and integration profile around
deterministic branch continuity for autonomous mutation:

- preserve unowned or unknown non-default branches as auditable unresolved work;
- require provider-authoritative branch inventory before branch deletion or closure;
- prevent implicit cleanup actions that are not backed by lossless supersession
  read-back; and
- keep autonomy continuation permissive only when ownership and disposition are
  unambiguous.

This strengthens practice alignment without broadening authorities or reducing
autonomy to per-task manual approval.

## Acceptance criteria

- [ ] AC-01: `spec/AUTONOMY_STANDARD.md` defines deterministic non-default
  branch and orphan handling in a dedicated section.
- [ ] AC-02: `profiles/subactor-semcod.profile.json` requires branch
  continuity/disposition restrictions for protected publish behavior.
- [ ] AC-03: `tests/test_autonomy.py` validates these standard/profile
  additions and keeps existing autonomy conformance coverage stable.
- [ ] AC-04: `examples/valid/project.autonomy.json` and
  `examples/dsl-manifest.json` contain updated authoritative digests for changed
  standard/profile artifacts.
- [ ] AC-05: Gate checks complete successfully on this branch (governance,
  checker validate, checker self-test, DSL check, compile/lint, Python tests).

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Pending: this is an in-progress implementation ticket. It must pass local
  governance, profile check, autonomy self-test, and unit tests before proposing
  publication evidence and merge cleanup.
