# Ticket 021: Subactor runtime ADOPT binding map in autonomy profile

- **ID**: ticket-021
- **Owner**: human:founder
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-08-15

## Goal and scope

Publish which Subactor runtime repositories ADOPT `wellmanifest/autonomy` (and
sibling packs) without inventing a parallel standard. Extend
`profiles/subactor-semcod.profile.json` ownership/bindings and document the
pointer to `subactor/platform/config/adopt/wellmanifest.v1.json`.

## Acceptance criteria

- [x] AC-01: Session authorization from Founder to map ADOPT and improve wellmanifest.
- [x] AC-02: Profile lists `subactor/platform`, `subactor/deployment`, `subactor/doctor-agent`, `subactor/www-sub-actor` as runtimeOwners.
- [x] AC-03: Observe bindings reference deployment PROCEDURES/TOPOLOGY and platform adopt map.
- [x] AC-04: `docs/SUBACTOR_RUNTIME_ADOPT.md` explains HOME vs ADOPT fail-closed.
- [x] AC-05: Digests for profile/examples updated; checks pass.
- [x] AC-06: Governance + autonomy_check + unittest pass.

## Participants

- Human participant: Founder (session authorization).
- Agent participant: [ai-cursor-composer.md](ai-cursor-composer.md)
