# Ticket 024: Guard continuation_check CLI against deeply nested JSON RecursionError

- **ID**: ticket-024
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Resolve the Validator advisory finding from `ticket-023` on `src/continuation_check.py`:
- Catch `RecursionError` during `json.loads()` in `_load_json_file()` and enforce an explicit iterative JSON nesting-depth ceiling (`MAX_CONTINUATION_JSON_DEPTH = 64`) so deeply nested JSON payloads (< 4 MiB) fail closed with `AUTONOMY-SYNTAX-001` instead of raising an uncaught `RecursionError` traceback.
- Add CLI regression tests for both >64 object nesting and C-parser recursion exhaustion in `tests/test_continuation.py`.
- Refresh the `src/continuation_check.py` parser-contract SHA-256 digest in `examples/dsl-manifest.json`.

## Acceptance criteria

- [x] AC-01: Scope is approved by a human owner (Validator advisory follow-up).
- [x] AC-02: `src/continuation_check.py` fails closed with `AUTONOMY-SYNTAX-001` on deeply nested JSON payloads without raising `RecursionError`.
- [x] AC-03: `unittest`, `ruff check`, `src/autonomy_check.py self-test`, `dsl_check.py validate examples/dsl-manifest.json`, `./project/governance-check.sh --actor ci`, and `wellman check` pass.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
