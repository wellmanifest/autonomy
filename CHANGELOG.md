# Changelog

## 0.7.0 - 2026-08-15

- Partitioned pre-approval protected checks: all non-circular checks must be in
  authoritative terminal success, while only approval-triggered checks may be
  deferred until the exact trusted App approval exists.
- Required a fresh successful attempt after the approval timestamp for every
  approval-triggered check, followed by the existing two stable protected
  convergence reads before merge.
- Added explicit-later and provider-coupled superseded-PR closure modes. Both
  require a protected path-complete lossless receipt; coupled closure also
  requires exact read-back of branch absence, closed/unmerged PR state and the
  preserved archive head.
- Derived the contract from `wellmanifest/logs#11/#12/#10`: Validator run
  `31849335166`, fresh post-approval governance run `31849434851`, protected
  receipt merge `ab268f932dbc09e5091fb8b7b4f4570790fa6254` and GitHub's
  coupled source-branch deletion/PR closure with archived predecessor head.
- Published exact Autonomy 0.7 head
  `f0f07c9d2852f63f99755d6c8ba182423f304d03` through hosted runs
  `31850464893` and `31850464947`, Validator run `31850486923`, App review
  `4941897120`, two stable protected reads and merge
  `39386e759968bea4ca80514e83249a9b5aadd4d1`, followed by protected closure
  merge `310fafeb60581c81e3aa8824fcc2fd61690bf88f`.

## 0.6.0 - 2026-08-15

- Required the protected Validator registry to equal the provider's complete
  effective ruleset, branch-protection, required-workflow and merge policy;
  stale or partial inventory fails closed.
- Made trusted approval start a new evidence epoch and required two stable
  exact-subject reads with authoritative terminal success before merge.
- Allowed bounded same-head retry only after post-approval convergence; changed
  head or base starts a new validation epoch.
- Added lossless superseded-work receipts and standing-policy deletion only for
  proven-equivalent branches, ordered before PR closure. Unresolved work keeps
  an open PR as explicit branch owner.
- Derived the contract from `wellmanifest/logs#8/#9`: premature Validator runs
  `31843668089` and `31844252756`, converged retries `31843844487` and
  `31844397273`, plus `GOV-BRANCH-LIFECYCLE-002` after closing a PR while
  preserving its branch.
- Published exact Autonomy 0.6 head
  `2f07112d012463c7b5c9ec008f69ac8ddbe38c4a` through hosted runs
  `31845381347` and `31845381421`, Validator run `31845403893`, App review
  `4941554180`, explicit merge
  `463e6996018a31b1a53f1f1b9ec056585e08ceb1`, read-back and cleanup.

## 0.5.0 - 2026-08-14

- Required a committed intent checkpoint before implementation and an explicit
  intent-only correction before any affected implementation scope expansion.
- Standardized moved-base recovery through a successor pull request, complete
  revalidation and preservation of published candidate history.
- Required exact version resolution and passing evidence for local CLI,
  container image, Compose, hosted CI and independent Validator contract
  consumers; unknown or omitted surfaces fail closed.
- Bound required-check authority to protected producer, triggering event,
  repository, exact head SHA and check name; ambiguous duplicate contexts fail
  closed and non-authoritative status cannot override the protected result.
- Allowed bounded provider-read fallback only when authority and subject
  bindings are preserved; rate limiting remains a degraded outcome.
- Derived the contract from the protected Deployment migration and published
  exact Autonomy 0.5 head `223960199d4d9564422f0d99b3321865cca376f4`
  through Validator run `31842212753`, App review `4941309883`, explicit merge
  `7e5988e5d07d9695eb2e610b7bd577d4beb3420b`, read-back and cleanup.

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
