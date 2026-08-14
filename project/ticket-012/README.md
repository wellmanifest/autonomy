# Ticket 012: Align root documentation with Autonomy 0.6

- **ID**: ticket-012
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Align the governance-owned root landing page and changelog with the already
published stable Autonomy 0.6 contract. Explain post-approval policy
convergence and lossless superseded-work disposition without changing any
normative, schema, profile, example, source or test artifact.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes this documentation-only
      update from exact protected `main@e8efa46`.
- [x] AC-02: README identifies stable 0.6.0 and explains effective-policy
      equality, the post-approval evidence epoch and two stable reads.
- [x] AC-03: README explains lossless delete-before-close disposition and open
      PR ownership for unresolved superseded work.
- [x] AC-04: CHANGELOG records Autonomy 0.6 and exact publication evidence.
- [x] AC-05: Only README, CHANGELOG and ticket governance paths change; all
      deterministic regression gates pass before publication.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted conformance run `31845956724` and remote lifecycle run `31845956732`
  passed on exact head `0a82aef6494a801396c673c53a01777ac1374d7d`.
- Validator run `31845983228` completed successfully and App review
  `4941595392` approved that exact head.
- The Validator App explicitly merged PR #22 as
  `4d2257e98aa881ddd8eba9e14207e22d6c395d63`; protected `main` read-back
  returned the same SHA and the source branch was deleted.
