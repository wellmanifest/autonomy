# Ticket 015: Repair Autonomy DSL artifact digest closure

- **ID**: ticket-015
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Repair the stale artifact digests published in the Autonomy 0.7 DSL manifest
and issue a semver patch release. Keep the v5 semantics unchanged while
advancing the release/profile binding to 0.7.1 and proving the external DSL
checker against every exact artifact byte.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes the repair from exact
      protected `main@ff11f595`.
- [x] AC-02: VERSION, DSL manifest, profile selection and version assertion
      advance coherently to 0.7.1 without a schema-generation change.
- [x] AC-03: Every DSL artifact digest equals the exact published candidate
      byte content; no stale digest remains.
- [x] AC-04: The Autonomy checker, JSON Schema validator and external
      Wellmanifest DSL checker all pass.
- [x] AC-05: Only the five declared implementation files and ticket governance
      paths change; root release docs remain a separate governance workstream.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted autonomy conformance run `31851601488` and remote lifecycle run
  `31851601480` passed on exact head
  `f76a502b78ec18b662834ba98b616a183eec2d03`.
- The expected `00:17 UTC` scheduled cycle had not been delivered by
  `00:45 UTC`; recovery used the same matrix `direct-scan` strategy in run
  `31854603326`, bounded above prior run ID `31854361196`.
- Validator App review `4942176742` approved that exact head and the protected
  policy converged after two stable reads.
- The Validator App explicitly merged PR #28 as
  `5a6289c7ed2bc1a752ee1851a70205b9be64c340`; protected `main` read-back
  returned the same SHA and the source branch was absent.
