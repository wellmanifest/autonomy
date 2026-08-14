# Ticket 006: Align root Autonomy 0.3 release documentation

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Replace the stale root `0.1.0-dev` description with the protected, stable
Autonomy 0.3 release state and summarize the practice-backed durability,
scheduled publication and deployment-source integrity guarantees without
changing normative artifacts.

## Acceptance criteria

- [x] AC-01: README identifies stable 0.3.0 and links the normative standard,
  schema, profile, architecture and conformance CLI as current entry points.
- [x] AC-02: Changelog records 0.2 practice-backed durability and 0.3 protected
  deployment-source integrity with exact protected publication references.
- [x] AC-03: Governance, existing unit tests and diff checks pass without any
  normative or executable artifact change.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted governance and Autonomy conformance checks passed on exact head
  `c20722625df526bee6a5fd1813fde5347d559206`.
- Validator run `31828838503` completed successfully; App review `4940151588`
  approved that same head.
- The Validator App explicitly merged PR #10 as
  `0349f3ae1806057febfb8343bb46652e8674c8a6`.
- Protected `main` read-back returned the same commit and the source branch was
  deleted.
