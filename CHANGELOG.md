# Changelog

## 0.4.0 - 2026-08-14

- Required exact runtime revision/artifact pins; membership in protected
  history alone is insufficient before loading effect-capable code.
- Prohibited supervisor configuration and executable paths from resolving
  through candidate or concurrently mutable development workspaces.
- Standardized prepare, validate, trigger-quiesce, switch, resume and rollback
  ordering with fail-stopped behavior and automatic post-rollout proof.
- Recorded the live linked-unit preflight failure with zero controller effects,
  protected `814e257` recovery, autonomous `subactor/autonom#17` publication
  through Validator run `31830719505`, App review `4940318952`, merge
  `88953aa58a48526caf1134ba40b04d0f39e3ff39` and the successful exact-pinned
  automatic cycle at `2026-08-14T18:57:40.427Z`.
- Published the exact 0.4 standard head through Validator run `31831392755`,
  App review `4940380603`, explicit merge
  `164a94e25550894e3c7ed468be316ab985219eff`, read-back and cleanup.

## 0.3.0 - 2026-08-14

- Required runtime code, effect-capable dependencies and authority-policy
  inputs to resolve from isolated, protected revision/digest-bound deployments.
- Required a supervisor outside the loaded controller to reject dirty or
  unprotected source before a cycle can perform any external mutation.
- Preserved the live zero-mutation registry-drift incident and detached policy
  recovery as immutable architecture evidence.
- Published the exact 0.3 head through Validator run `31828176479`, App review
  `4940097631`, explicit merge
  `d45d0d2aa31af45a23ea712e9a6be9e99a01b087`, read-back and cleanup.

## 0.2.0 - 2026-08-14

- Standardized durable at-least-once delivery, exact idempotency bindings,
  non-renewable leases, crash-safe checkpoints and bounded dead letters.
- Required an independent watchdog, per-repository outcome isolation, one
  digest-bound registry and explicit exact-head Validator App publication.
- Recorded automatic Subactor canary, hardened lease/recovery and receipt
  durability evidence from protected runtime PRs #13 through #15.
- Proved scheduled Validator publication for this repository in run
  `31827270068`, exact-head App review `4940020686` and merge
  `94c73bf273da3bea71d7502e73ba200b82d216d1`.

## Unreleased

- Established the governed repository baseline for the Wellmanifest Autonomy
  standard.
- Reserved the initial `0.1.0-dev` contract surface for standing grants,
  agent-role separation, bounded change budgets, exact-head merge gates, and
  autonomous task continuation.
