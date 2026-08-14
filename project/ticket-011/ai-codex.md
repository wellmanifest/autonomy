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
- Promoted the closed manifest and profile contracts to v4 / stable 0.6.0.
- Added a protected post-approval gate that discovers the effective repository
  policy, rejects registry drift, starts a new evidence epoch, requires two
  stable reads and rebinds the complete merge subject.
- Added lossless superseded-work disposition: exact predecessor/successor and
  content receipts, standing-policy deletion only for proven-equivalent work,
  delete-before-close ordering, and open-PR ownership for unresolved work.
- Added deterministic schema/checker enforcement and mutation tests for every
  newly observed failure mode; all 32 unit tests and every local conformance
  gate pass.
- Updated the architecture, state flow, Subactor/Semcod publication binding,
  example manifest, DSL schema version and exact artifact digests.
- Observed exact-head hosted checks, Validator run `31845403893`, App review
  `4941554180`, explicit merge
  `463e6996018a31b1a53f1f1b9ec056585e08ceb1`, protected-main read-back and
  source branch deletion.

## Blockers

- None. Autonomy 0.6 is merged; this governance-only successor records terminal
  state and immutable publication receipts.
- New authority remains required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.
