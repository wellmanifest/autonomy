# Ticket 023: Harden continuation_check against unhashable JSON, non-dict payloads, and unsafe file I/O

- **ID**: ticket-023
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Harden `src/continuation_check.py` so malformed or adversarial JSON payloads fail closed with deterministic diagnostic codes instead of raising uncaught Python runtime exceptions, and secure CLI file loading:
- Guard membership checks (`riskTier`, `requestedDecision`, `consentSource`, `actor.kind`, `decision`, `action`, `repository`) with `isinstance(..., str)` before set lookups to prevent `TypeError: unhashable type` on nested dicts/lists.
- Reject non-dict `humanRequest` (`SC-009`), non-dict `humanResponse` (`SC-011`), non-dict adoption records (`SC-008`), non-string/blank `publicationKey` (`SC-004`), and malformed `check_fleet()` lists/rows (`SC-008`).
- Harden `continuation_check.py` CLI file reads with `O_NOFOLLOW | O_NONBLOCK`, `S_ISREG`, a 4 MiB byte cap, duplicate-key rejection, and `NaN`/`Infinity` rejection, returning `AUTONOMY-SYNTAX-001` on invalid input files.
- Update the `src/continuation_check.py` SHA-256 artifact digest in `examples/dsl-manifest.json` and expand `tests/test_continuation.py`.

## Acceptance criteria

- [x] AC-01: Scope is approved by a human owner (continuous hardening/testing session).
- [x] AC-02: `check_human_request`, `check_human_response`, `check_decision`, `check_adoption`, `check_fleet`, and `main()` fail closed without uncaught exceptions on unhashable/non-dict JSON values, symlinks, duplicate keys, and non-finite constants.
- [x] AC-03: `unittest`, `src/autonomy_check.py self-test`, `dsl_check.py validate examples/dsl-manifest.json`, `./project/governance-check.sh --actor agent`, and `wellman check` pass with all touched modules under 500 lines.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
