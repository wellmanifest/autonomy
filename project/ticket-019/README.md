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
- make tasks that genuinely require human help explicit, digest-bound and
  fail-closed while preserving the existing autonomous path;
- keep autonomy continuation permissive only when ownership and disposition are
  unambiguous.

This strengthens practice alignment without broadening authorities or reducing
autonomy to per-task manual approval.

## Acceptance criteria

- [x] AC-01: `spec/AUTONOMY_STANDARD.md` defines deterministic non-default
  branch and orphan handling in a dedicated section.
- [x] AC-02: `profiles/subactor-semcod.profile.json` requires branch
  continuity/disposition restrictions for protected publish behavior.
- [x] AC-03: `tests/test_autonomy.py` validates these standard/profile
  additions and keeps existing autonomy conformance coverage stable.
- [x] AC-04: `examples/valid/project.autonomy.json` and
  `examples/dsl-manifest.json` contain updated authoritative digests for changed
  standard/profile artifacts.
- [x] AC-05: Gate checks complete successfully on this branch (governance,
  checker validate, checker self-test, DSL check, compile/lint, Python tests).
- [x] AC-08: The supervisor-continuation profile defines the versioned
  human-assistance request/response boundary, including exact subject binding,
  expiry and frozen effects.
- [x] AC-09: The continuation checker rejects malformed or mismatched human
  requests/responses, effects while waiting, expired consent and LLM-inferred
  consent.
- [x] AC-10: The standard, Subactor profile, operational documentation, examples
  and tests explain when human help is required without widening the standing
  grant.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Pending: this is an in-progress implementation ticket. It must pass local
  governance, profile check, autonomy self-test, and unit tests before proposing
  publication evidence and merge cleanup.

## Supervisor continuation extension

SESSION_EXECUTION_AUTHORIZATION: Founder requested improving standards in wellmanifest and adopting them across Subactor and related projects on 2026-09-05. The current default branch still reserves this matching integration ticket. Extend its convergence scope with a separately versioned continuation profile and conformance fixtures.

- [x] AC-06: deterministic checks reject human-only routing when authorized independent validation is available, unbounded unchanged reassessment and false completion.
- [x] AC-07: fleet inventory distinguishes applicable, adopted, verified and blocked consumers using exact revision/digest and runtime evidence; missing repositories cannot be counted as covered.

## Human-assistance extension

SESSION_EXECUTION_AUTHORIZATION: Founder requested a standard for tasks that
require human help on 2026-09-15. The matching integration ticket is extended,
not duplicated: `wellmanifest/autonomy` already owns the autonomy boundary and
the supervisor continuation checker. The extension adds a typed,
digest-and-subject-bound request/response protocol and a fail-closed waiting
state; it does not read secrets, grant authority, or publish to external
systems.
