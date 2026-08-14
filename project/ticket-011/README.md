# Ticket 011: Require post-approval convergence and lossless superseded-branch disposal

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.6 from two protected `wellmanifest/logs` publication
incidents. The standard must treat Validator App approval as a state-changing
operation that can trigger new required checks, reconcile the protected
registry with the effective repository policy, and dispose of superseded
branches without either losing unique work or creating an orphan branch.

The target design remains autonomous: no per-PR human approval is added. The
publisher waits for a post-approval evidence epoch, then merges only after the
effective exact-head policy has converged. A standing lifecycle policy may
delete a superseded branch only after deterministic lossless-disposition proof;
otherwise its PR remains open as the branch owner.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes this bounded standard
      revision from exact protected `main@f756839`, ten implementation files,
      three components and no runtime dependency.
- [x] AC-02: Manifest v4 requires protected discovery of the effective required
      check set and rejects registry drift before review or merge.
- [x] AC-03: App approval starts a new evidence epoch; every approval-triggered
      exact-head check must reach authoritative terminal success before merge,
      followed by a final head/base/approval/policy rebind.
- [x] AC-04: Superseded work has a closed lossless disposition: prove the
      successor merged, archive all required evidence, delete only a proven
      equivalent branch before closing its PR, and keep unresolved work open.
- [x] AC-05: Checker and tests reject premature merge, stale policy inventory,
      closed-PR orphan creation, unproved branch deletion and incomplete
      supersession bindings.
- [x] AC-06: Spec, schema, profile, example, architecture and logic flow align
      at stable version 0.6.0 and pass every deterministic conformance gate.

## Practice evidence

- `wellmanifest/logs#8`: Validator run `31843668089` approved exact head
  `a52a7f3f12b379847d8fbf4d598649b601f5c708`, which triggered governance run
  `31843804587`. The first merge attempt preceded that check's completion;
  exact-head retry `31843844487` merged only after convergence.
- `wellmanifest/logs#9`: Validator run `31844252756` reproduced the same race.
  Approval review `4941462599` triggered governance run `31844363274`; retry
  `31844397273` succeeded after terminal success.
- Closing predecessor `logs#7` while preserving its branch caused
  `GOV-BRANCH-LIFECYCLE-002` in hosted run `31844139952`. Reopening the PR
  restored ownership. The current policies therefore require an explicit,
  lossless branch-disposition order.

## Risks

- This is a manifest/profile v4 boundary. Existing v3 adopters remain valid
  historical records but cannot claim Autonomy 0.6 conformance.
- Lossless disposal does not mean matching only the five implementation files;
  governance and audit evidence must also be archived or explicitly retained.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
