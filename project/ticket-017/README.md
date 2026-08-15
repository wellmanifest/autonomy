# Ticket 017: Standardize heartbeat correlation and idempotent effects

- **ID**: ticket-017
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-15

## Goal and scope

Turn the production evidence from Autonomy 0.7.1 publication into enforceable
Autonomy 0.8 contracts. A conforming project must expose scheduler heartbeat
freshness independently from recovery, select only the exact post-dispatch run
bound to its correlation identity, and reconcile repeated effects to one
authoritative external receipt without issuing a second review or merge.

## Acceptance criteria

- [x] AC-01: The user's continuation request authorizes implementation from
      exact protected `main@0f5f80ab` without a second per-PR confirmation.
- [x] AC-02: Manifest v6 requires a scheduler heartbeat SLO, protected
      missed-cycle monitoring and explicit late-delivery deduplication; manual
      recovery cannot be counted as scheduler-liveness evidence.
- [x] AC-03: Manifest v6 requires pre-dispatch observation boundaries and
      exact repository, target, head, strategy and correlation bindings for
      both direct and matrix child run selection.
- [x] AC-04: Manifest v6 requires at most one authoritative external effect;
      an `already-applied` outcome is valid only after exact external
      read-back, while stale, ambiguous and closed-unmerged subjects fail
      closed.
- [x] AC-05: The Subactor/Semcod profile, valid and invalid examples,
      architecture and logic flow encode the observed missed heartbeat,
      bounded recovery and duplicate no-op publication evidence precisely.
- [x] AC-06: Governance, semantic, schema, unit, compile, lint and external
      DSL validation pass with exact artifact digests and no new runtime
      dependency.
- [x] AC-07: Publication occurs only through independent exact-head Validator
      App review, explicit protected merge, read-back and branch cleanup.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)

## Publication evidence

- Hosted autonomy conformance run `31856137043` and remote lifecycle run
  `31856137020` passed on exact head
  `c86ec6dbf40783481afb9ca95801251bd428db42`.
- The dispatch helper captured run-ID boundary `31855488871` and selected only
  post-boundary Validator run `31856175299` with correlation
  `autonomy-pr-32-ticket-017-c86ec6dbf4`.
- Validator App review `4942309733` approved that exact head; its deterministic
  verdict remained authoritative while the optional LLM advisory was degraded.
- The protected policy converged after two stable reads and the Validator App
  explicitly merged PR #32 as
  `69d22e41af70e16e78105ae8ae008b53652aa6c0`.
- Protected `main` read-back returned the same merge SHA and the source branch
  was absent.
