# Ticket 014: Align root docs with stable Autonomy 0.7

- **ID**: ticket-014
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Align the governance-owned root landing page and changelog with the already
published stable Autonomy 0.7 contract. Record the practice-backed
pre-approval check partition and provider-coupled superseded-PR disposition
without changing normative, executable or integration artifacts.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes this documentation-only
      update from exact protected `main@310fafeb`.
- [x] AC-02: README identifies stable 0.7.0 and distinguishes pre-approval
      readiness from fresh post-approval convergence.
- [x] AC-03: README models both explicit-later and provider-coupled closure
      without weakening lossless archival or exact read-back.
- [x] AC-04: CHANGELOG records Autonomy 0.7 and exact publication evidence.
- [x] AC-05: Only README, CHANGELOG and ticket governance paths change; all
      deterministic regression gates pass before publication.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted autonomy conformance run `31851056165` and remote lifecycle run
  `31851056226` passed on exact head
  `9a9dd714c80b11747daf8721bdb96a01ec699392`.
- Validator run `31851081469` completed successfully and App review
  `4941939096` approved that exact head after two stable protected reads.
- The Validator App explicitly merged PR #26 as
  `e7ebaafde55832ef09df2ee196b154cd06fd5eed`; protected `main` read-back
  returned the same SHA and the source branch was absent.
