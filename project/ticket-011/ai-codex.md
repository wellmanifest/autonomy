---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-011
---
# Participant: codex (AI agent)

## Understanding

The protected repository can change after App review: GitHub review events may
start required workflows. A green check snapshot from before approval is
therefore not sufficient evidence for merge. The Validator registry is also
only a declared expectation; it must agree with the effective ruleset and
branch-protection policy or publication must stop.

Superseded PR cleanup has a second cross-policy race. Closing an unmerged PR
while preserving its branch satisfies evidence-preservation policy but creates
an orphan rejected by remote lifecycle policy. Autonomy needs one deterministic
standing disposition: delete only after lossless equivalence proof and before
closing, otherwise keep the PR open as owner.

## Execution plan

1. Commit this exact intent before any normative implementation.
2. Add manifest v4 publication-convergence and superseded-work contracts.
3. Update the checker, valid example and Subactor/Semcod runtime profile.
4. Add regressions for policy drift, approval-triggered checks and every branch
   disposition failure mode.
5. Align the normative spec and architecture flows, then publish exact-head
   evidence through the independent Validator App.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Bound the practice record to two exact `logs` publication races and the
  remote branch-lifecycle contradiction before implementation.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
