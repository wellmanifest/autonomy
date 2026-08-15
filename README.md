# wellmanifest/autonomy

Normative Wellmanifest domain pack for autonomous software-development
continuation by a governed fleet of Subactor agents and Semcod tools.

After a project adopts this standard and an authorized principal issues an
active standing autonomy grant, qualifying work may be selected, implemented,
validated, opened as a pull request, approved by an independent trusted
Validator App, merged, verified, and followed by the next task without a human
approval on every pull request.

The grant is bounded. It cannot authorize its own renewal or expansion, and an
implementing agent cannot validate or approve its own change. Out-of-scope,
high-risk, destructive, secret-bearing, or ambiguous work fails closed and is
escalated.

## Repository boundary

This repository owns:

- the normative autonomy manifest and standing-grant semantics;
- agent-role separation, risk budgets, merge gates, and continuation rules;
- a Subactor/Semcod integration profile;
- deterministic conformance fixtures and a dependency-free validator.

This repository does not host an agent, GitHub App, queue, scheduler, LLM,
repository mirror, or mutation runtime. Those systems remain owned by
`subactor/*` and `semcod/*` and adopt this domain pack.

## Current entry points

- `spec/AUTONOMY_STANDARD.md` — normative requirements;
- `schemas/autonomy-manifest.schema.json` — strict JSON contract;
- `profiles/subactor-semcod.profile.json` — integration profile;
- `src/autonomy_check.py` — deterministic conformance CLI;
- `docs/ARCHITECTURE.md` and `docs/LOGIC_FLOW.md` — deployment guidance.

## Operational proof boundary

Static schema/checker success proves contract conformance, not a live autonomous
execution path. Runtime conformance additionally requires a fresh protected
scheduler heartbeat, automatic trigger, claim, validation, protected
publication, effect reconciliation, read-back, cleanup and independently
observed missed-cycle recovery receipts. Manual or recovery dispatch remains
execution/diagnostic evidence and does not substitute for scheduler liveness.

The Subactor reference runtime has exercised the durable timer/controller path,
exact-head Validator App merge, checkpoint recovery and an exact-pinned runtime
rollout. Its protected old runtime autonomously merged the rollout PR through
Validator run `31830719505`; after deployment, the next natural timer cycle at
`2026-08-14T18:57:40.427Z` ran from exact merge
`88953aa58a48526caf1134ba40b04d0f39e3ff39` with `ok=true`,
`dry_run=false` and zero mutations. The Wellmanifest repository was also
published by the independent scheduled Validator target in run `31827270068`
without a manual dispatch.

Status: stable `0.8.0`, canonical manifest
`wellmanifest.autonomy/manifest/v6`. The selected Subactor/Semcod profile has
exact SHA-256
`3a5317269418dd31e09b2e630edaf59a4b994e24df9eb2f6bca59f194c81ba64`,
and all thirteen DSL artifacts bind their exact published bytes.

Autonomy 0.8 makes scheduler liveness explicit. The execution plane declares
an expected heartbeat interval and delivery grace; every expected cycle emits
an external `scheduler-heartbeat` receipt. A protected independent monitor
marks a missed cycle degraded and starts or reconciles one bounded recovery.
Successful recovery does not repair the missing heartbeat. If the scheduled
delivery arrives late, both paths deduplicate through one idempotency subject.

Provider invocation identity is also closed. Before dispatch, the controller
records the greatest visible provider run or equivalent event. It then accepts
only a post-boundary run that exactly binds strategy, repository, target, head
SHA and correlation ID. The same correlation must reach an effect-capable
matrix child. Workflow names, PR titles and timing are not identity; zero or
multiple ambiguous matches fail closed.

Every mutation converges to at most one authoritative external effect. Success
is `applied` or `already-applied`, and the latter requires external read-back
of the exact subject. An already merged publication additionally binds its
pull request, base, trusted approval, merge commit and timestamp and never
receives a second review or merge. Closed-unmerged, stale, missing-receipt and
ambiguous subjects remain failures.

These rules come from live publication behavior. The expected `00:17 UTC`
cycle for Autonomy 0.7.1 was absent through `00:45 UTC`; recovery captured run
boundary `31854361196`, selected matrix run `31854603326`, and merged exact
head `f76a502b` through App review `4942176742`. This proved recovery execution,
not scheduler delivery. Validator 0.6.48 then proved the duplicate terminal
path: run `31854007167` read back approval `4942134199` and merge
`3fe9659011372b734bc24302ed83eb0b49f9c95f` without another review or merge.

The 0.8 standard itself was published from exact head
`c86ec6dbf40783481afb9ca95801251bd428db42`. Hosted conformance runs
`31856137043` and `31856137020` passed; post-boundary Validator run
`31856175299` issued deterministic App review `4942309733`, converged twice and
merged PR #32 as `69d22e41af70e16e78105ae8ae008b53652aa6c0`.
Its optional LLM advisory was unavailable, demonstrating that deterministic
approval authority remains sufficient. Governance closure then passed run
`31856383207`, review `4942321841` and merge
`85eea5f07379ceb4f73e469a7c979c61637f748e`.

Autonomy 0.8 retains the earlier boundaries: effective-policy inventory,
post-approval evidence epochs, two stable reads, lossless superseded-work
disposition, plan-first intent history, successor PRs instead of history
rewrite, complete contract-consumer migration, authoritative check provenance,
exact runtime pins and separation of implementer, validator and publisher.
