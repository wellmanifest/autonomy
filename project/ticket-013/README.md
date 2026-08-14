# Ticket 013: Model platform-coupled superseded PR closure and approval-triggered preflight

- **ID**: ticket-013
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-14

## Goal and scope

Promote Autonomy 0.7 from two failures observed while publishing
`wellmanifest/logs`. First, the canonical dispatcher waited before review for
`governance / governance / enforce`, although that check is created only by a
trusted App approval. Second, deleting the proven-equivalent source branch of
open PR #10 caused GitHub to close the PR in the same platform operation, so
the v0.6 prescription to close it in a later controller mutation could not be
executed literally.

The revision must preserve the original safety properties. Pre-approval must
still require every non-circular check to succeed; approval-triggered attempts
must be ignored before approval and pass afterward. Superseded work must still
have a protected, path-complete lossless receipt before deletion. A provider
may classify immediate PR closure as a platform-coupled effect only after
read-back proves the branch absent, the PR closed and unmerged, and the durable
archive ref still bound to the predecessor head.

No Validator runtime, GitHub workflow, branch policy or root release notes are
changed here. Runtime implementation belongs in `subactor/validator-agent`;
root README/CHANGELOG alignment will use a governance-only follow-up after the
standard is published.

## Acceptance criteria

- [x] AC-01: The user's autonomous continuation authorizes this bounded
      practice-backed revision from protected `main@2d08d74`, ten
      implementation files, three components and no runtime dependency.
- [ ] AC-02: Manifest/profile v5 distinguish pre-approval non-circular checks
      from approval-triggered checks and require a new post-approval attempt.
- [ ] AC-03: Manifest/profile v5 model explicit later close and immediate
      platform-coupled close without weakening lossless proof or read-back.
- [ ] AC-04: The checker rejects waiting for circular checks before approval,
      reusing pre-approval attempts, unproved deletion and unverified coupled
      closure/archive state.
- [ ] AC-05: Spec, schema, profile, examples and operational documentation
      align at stable version `0.7.0`.
- [ ] AC-06: Governance, conformance, self-tests, unit tests, compile and Ruff
      all pass before publication.

## Practice evidence

- On logs PR #11, `dispatch-direct-pr.sh --wait-checks` stalled on missing
  `governance / governance / enforce` before review. The wait was interrupted;
  Validator run `31849335166` then correctly approved exact head `f8ec0d8`,
  required approval-triggered run `31849434851`, observed two stable reads and
  merged as `3e1bf6e4`.
- Logs PR #12 integrated the complete predecessor-content manifest and
  lossless receipt as protected merge `ab268f932dbc09e5091fb8b7b4f4570790fa6254`.
  Deleting branch `ticket-005-logs-v02-docs` while PR #10 was open immediately
  changed the PR to closed/unmerged at `2026-08-14T23:18:40Z`; no explicit
  close request was sent. `refs/pull/10/head` remained bound to exact head
  `4c235afecdf2c6f4da41fce98293e71228ae93b3`.

## Risks

- Platform-coupled close is provider capability, not permission to bundle
  arbitrary mutations. Unknown provider behavior still fails closed.
- A coupled close is valid only after integrated archival proof and complete
  read-back; it never authorizes deletion of unresolved unique work.

## Participants

- Human participant: the session owner authorized autonomous continuation; no
  `user-*` file was created or modified.
- Agent participant: [ai-codex.md](ai-codex.md)
