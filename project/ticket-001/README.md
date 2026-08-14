# Ticket 001: Define autonomous Subactor agent integration standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
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

- [ ] AC-01: The normative standard defines a standing grant that explicitly
  permits routine PR creation, trusted automated approval, merge, verification,
  and next-task selection without per-PR human consent.
- [ ] AC-02: A closed Draft 2020-12 JSON Schema defines repository subject,
  grant, roles, authority, risk, budgets, lifecycle, gates, and receipts.
- [ ] AC-03: Doctor/observer, planner, implementer/repair, validator, publisher,
  and auditor roles have non-escalating authority and enforce separation of
  duties; an implementer cannot validate or approve its own change.
- [ ] AC-04: Risk tiers, excluded effects, lease expiry, kill switch, retry,
  cooldown, cost/change budgets, and escalation rules fail closed.
- [ ] AC-05: Automated merge requires current base, exact PR head, trusted
  deterministic checks, independent Validator App evidence, read-back, and
  branch cleanup.
- [ ] AC-06: A bounded continuation loop selects runnable backlog work,
  performs one mutation per cycle, records evidence, and proceeds to the next
  task without silently treating waiting or skipped work as success.
- [ ] AC-07: A versioned Subactor/Semcod profile maps existing repositories and
  tools to evidence, planning, repair, validation, publication, and audit while
  respecting HOME/ADOPT ownership.
- [ ] AC-08: Valid and invalid fixtures plus a dependency-free CLI expose
  stable `AUTONOMY-*` diagnostic codes for structural and semantic violations.
- [ ] AC-09: Architecture and logic-flow documentation explain adoption,
  multi-agent trust boundaries, PR lifecycle, recovery, and escalation.
- [ ] AC-10: Governance, unit, schema, semantic, DSL-manifest, syntax, and
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
