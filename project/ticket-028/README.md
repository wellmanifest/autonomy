# Ticket 028: Add human manual control and autonomy failure override to autonomy standard

- **ID**: ticket-028
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-11-24
- **Authorization**: `SESSION_EXECUTION_AUTHORIZATION` (user explicitly instructed not to revert personal merges made when automation failed, to allow human merging, and to update Wellmanifest standards to account for autonomy failures and permit manual control).

## Goal and scope

Extend `spec/AUTONOMY_STANDARD.md` with Section `6.2 Human manual control and autonomy failure override` (plus cross-reference in Section 8), update the corresponding specification SHA-256 digest in `examples/dsl-manifest.json`, and add unit test assertions in `tests/test_autonomy_profile_docs.py` — ensuring autonomy never locks out the authenticated human owner on failure while preserving strict AI-agent non-self-merge guardrails.

## Acceptance criteria

- [x] AC-01: `spec/AUTONOMY_STANDARD.md` adds Section `6.2` defining `autonomy-degraded` owner manual steering/merge fallback, non-revert preservation of human manual merges, distinct `manual-owner-override` audit provenance, and unchanged AI-agent boundaries.
- [x] AC-02: `examples/dsl-manifest.json` binds the exact updated SHA-256 digest of `spec/AUTONOMY_STANDARD.md`.
- [x] AC-03: `tests/test_autonomy_profile_docs.py` verifies Section `6.2` under 500 lines and all `unittest`, `autonomy_check.py self-test`, `compileall`, and `wellman check` checks pass.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
