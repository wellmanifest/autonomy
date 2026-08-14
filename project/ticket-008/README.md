# Ticket 008: Align root documentation with Autonomy 0.4

- **ID**: ticket-008
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Align governance-owned root documentation with the already published stable
Autonomy 0.4 release. Describe exact-runtime pinning, supervisor isolation,
quiesced rollout/rollback and the live Subactor proof without changing any
normative, schema, profile or executable artifact.

## Acceptance criteria

- [x] AC-01: README identifies stable 0.4.0 and summarizes the deployment and
  operational-proof boundary accurately.
- [x] AC-02: CHANGELOG records the practice evidence and protected publication
  identifiers for 0.4.0.
- [x] AC-03: No normative, schema, profile, example, source or test file changes.
- [x] AC-04: Governance and regression checks pass before protected publication.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Local and hosted governance, 26 tests, self-test, compilation, Ruff and diff
  checks passed on exact head `14a86cd699677a29194404cae8c910e4182c3834`.
- Validator run `31831972095` completed successfully and App review
  `4940427343` approved that exact head.
- The Validator App explicitly merged PR #14 as
  `eab9c7b8cb99560d022e35acf12ea04b5ec708e6`.
- Protected `main` read-back returned the same merge commit and the source
  branch was deleted.
