# Ticket 025: Modularize autonomy_check under 500 lines and harden JSON, profile, and pointer bounds

- **ID**: ticket-025
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Split `src/autonomy_check.py` (2201 lines) and `tests/test_autonomy.py` (623 lines) into focused modules strictly under 500 lines each while preserving the full CLI and Python API surface, hardening JSON/profile loading (`O_NOFOLLOW`, 4 MiB cap, duplicate-key/NaN rejection, 64-level nesting depth), guarding non-object profile JSON against `AttributeError`, enforcing RFC 6901 array indices and non-symlink traversal in `apply_invalid_case` and `iter_json_paths`, tightening RFC 3339 timestamp and path-glob validation, and synchronizing `examples/dsl-manifest.json`.

## Acceptance criteria

- [x] AC-01: Every owned Python file in `src/` and `tests/` is strictly under 500 lines while preserving `autonomy_check` public exports and CLI behavior.
- [x] AC-02: Symlinks, duplicate JSON keys, >64 JSON nesting depth, non-object profile files, negative/leading-zero JSON Pointer array indices, `..` path-glob segments, space-separated timestamps, and empty validation directories fail closed without uncaught exceptions.
- [x] AC-03: `unittest`, `autonomy_check.py self-test`, `dsl_check.py`, `./project/governance-check.sh`, and `wellman check` pass with synchronized `examples/dsl-manifest.json` parser-contract digests.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
