---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-013
---
# Participant: codex (AI agent)

## Understanding

Autonomy 0.6 captured the right safety goals but over-specified GitHub's
mutation sequence and under-specified the pre-approval check partition. GitHub
can close an open PR as a coupled effect of deleting its branch, while an
approval-triggered check cannot be a prerequisite for the approval that
creates it. Both must become explicit closed-contract states instead of
operator folklore.

## Execution plan

1. Commit this plan and delivery contract before changing the standard.
2. Promote manifest/profile contracts to v5 and stable version 0.7.0.
3. Require pre-approval check partitioning and post-approval attempt freshness.
4. Add provider-coupled close semantics with lossless archival and read-back.
5. Add negative tests and align spec, examples and operational diagrams.
6. Run every deterministic gate, freeze the exact head and publish only
   through independent Validator App review and merge.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Read the protected Autonomy 0.6 contract and bound this plan to the exact
  logs PR #11/#12 publication and PR #10 disposal evidence.
- No implementation file is changed by this plan commit.
- Promoted the schema, manifest, profile, DSL metadata and conformance checker
  to v5 / stable 0.7.0.
- Added a closed pre-approval policy that requires every non-circular check to
  pass, defers only approval-triggered checks, and requires their fresh attempt
  after the exact approval timestamp.
- Added explicit-later and provider-coupled close modes. Both require an
  integrated lossless receipt; coupled close additionally requires read-back of
  branch absence, closed/unmerged PR state and the preserved archive head.
- Updated the Subactor/Semcod profile, normative spec, architecture and logic
  flow, plus negative regressions for incomplete or unsafe projections.
- Passed JSON Schema Draft 2020-12 validation, conformance, self-test, 32 unit
  tests, compile, Ruff, governance and whitespace checks.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
