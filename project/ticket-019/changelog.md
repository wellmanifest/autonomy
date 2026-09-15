# Ticket Changelog (ticket-019)

## [0.2.0] - 2026-09-15

- Defined `wellmanifest.autonomy/human-assistance/v1` for bounded human help.
- Bound requests and responses to repository, ticket, head, base and profile
  digests; expired or pending requests freeze effect-capable actions.
- Added deterministic request/response checks, CLI entry points and Subactor
  profile restrictions; LLM output remains advisory and cannot be consent.
- Repaired the DSL manifest's typed-source LLM decision boundary and refreshed
  all changed artifact digests.

## [0.1.0] - 2026-08-15

- Initial governance scaffold created.
- No human participant identity or content was generated.
- Added deterministic branch continuity and orphan handling to
  `spec/AUTONOMY_STANDARD.md` as a required continuation discipline.
- Added `orphan-branch-preservation-policy` and
  `provider-branch-inventory-authority` to Subactor/Semcod publish restrictions.
- Added corresponding checks in `tests/test_autonomy.py` for normative and
  profile requirements.
