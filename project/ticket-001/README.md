# Ticket 001: Define autonomous Subactor agent integration standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Create a reusable Wellmanifest standard that lets an adopted project continue
development through a governed fleet of Subactor agents and Semcod tools. An
active standing grant replaces per-pull-request human approval for qualifying
changes while retaining independent validation, exact-head binding, risk and
resource budgets, audit receipts, revocation, and fail-closed escalation.

The repository is a Wellmanifest `domain_pack`. Runtime controllers, agent
services, queues, GitHub Apps, and Semcod executors remain in their owning
repositories and adopt this standard.

## Acceptance criteria

- [x] AC-01: The normative standard defines a standing grant that explicitly
  permits routine PR creation, trusted automated approval, merge, verification,
  and next-task selection without per-PR human consent.
- [x] AC-02: A closed Draft 2020-12 JSON Schema defines repository subject,
  grant, roles, authority, risk, budgets, lifecycle, gates, and receipts.
- [x] AC-03: Doctor/observer, planner, implementer/repair, validator, publisher,
  and auditor roles have non-escalating authority and enforce separation of
  duties; an implementer cannot validate or approve its own change.
- [x] AC-04: Risk tiers, excluded effects, lease expiry, kill switch, retry,
  cooldown, cost/change budgets, and escalation rules fail closed.
- [x] AC-05: Automated merge requires current base, exact PR head, trusted
  deterministic checks, independent Validator App evidence, read-back, and
  branch cleanup.
- [x] AC-06: A bounded continuation loop selects runnable backlog work,
  performs one mutation per cycle, records evidence, and proceeds to the next
  task without silently treating waiting or skipped work as success.
- [x] AC-07: A versioned Subactor/Semcod profile maps existing repositories and
  tools to evidence, planning, repair, validation, publication, and audit while
  respecting HOME/ADOPT ownership.
- [x] AC-08: Valid and invalid fixtures plus a dependency-free CLI expose
  stable `AUTONOMY-*` diagnostic codes for structural and semantic violations.
- [x] AC-09: Architecture and logic-flow documentation explain adoption,
  multi-agent trust boundaries, PR lifecycle, recovery, and escalation.
- [x] AC-10: Governance, unit, schema, semantic, DSL-manifest, syntax, and
  optional-container validation pass with recorded evidence.

## Participants

- Human participant: unresolved; no user-owned participant file was created.
- Agent participant: [ai-codex.md](ai-codex.md)

## Non-goals

- Hosting or implementing Subactor/Semcod runtime services in Wellmanifest.
- Giving an LLM, observer, digital twin, or diagnostic tool direct mutation or
  merge authority.
- Allowing a grant to renew, widen, or disable its own safety boundary.
- Automating secrets, destructive infrastructure, billing, legal, identity,
  security-critical, or otherwise excluded changes under the default profile.

## Validation evidence

- Published new-project governance adoption lock: 34 of 34 managed hashes
  match immutable revision `4d0a61837245b2906ce19c75c050fea1bc12adf2`.
- Governance: PASS with zero errors and warnings.
- Draft 2020-12 schema: valid manifest and Subactor/Semcod profile PASS.
- Autonomy semantic validator: valid manifest/profile and bundled mutation
  self-test PASS.
- Unit suite: 16 tests PASS, including self-approval, expiry, head binding,
  mandatory exclusions, malformed input, profile ownership, and path escape.
- Wellmanifest DSL manifest, artifact digests, help pages, standards lock, and
  controlled publication tier: PASS.
- Ruff, Python compilation, JSON parsing, Markdown links, diff whitespace,
  secret patterns, and local absolute-path scan: PASS.
- Runtime inventory: all 19 declared runtime-owner repositories and all 26
  profile contract references were present during local conformance research.
- Networkless, read-only Python container self-test: PASS using an image pinned
  by SHA-256 digest.

## Publication state

Local implementation is complete and validated. The user's request
authorizes public repository creation, branch push, and pull-request creation.
The ticket remains `IN_PROGRESS` through exact-head protected checks and
independent review. Publication PR:
<https://github.com/wellmanifest/autonomy/pull/1>.
