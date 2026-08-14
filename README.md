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
execution path. Runtime conformance additionally requires fresh non-manual
trigger, claim, validation, protected publication, read-back, cleanup and
watchdog recovery receipts. Manual or agent-initiated workflow dispatch remains
publication/diagnostic evidence and does not substitute for scheduler liveness.

The Subactor reference runtime has exercised the durable timer/controller path,
exact-head Validator App merge, checkpoint recovery and an exact-pinned runtime
rollout. Its protected old runtime autonomously merged the rollout PR through
Validator run `31830719505`; after deployment, the next natural timer cycle at
`2026-08-14T18:57:40.427Z` ran from exact merge
`88953aa58a48526caf1134ba40b04d0f39e3ff39` with `ok=true`,
`dry_run=false` and zero mutations. The Wellmanifest repository was also
published by the independent scheduled Validator target in run `31827270068`
without a manual dispatch.

Status: stable `0.5.0`. Autonomy 0.5 requires a committed intent checkpoint
before implementation and treats a moved protected base as a new successor PR,
not permission to rewrite published candidate history. Every contract migration
must inventory and pass its local CLI, container image command, Compose
override, hosted CI checkout and independent Validator against an exact
allowlisted version before execution.

Required checks are authoritative only when their protected registry binding
uniquely matches producer, event, repository, exact head SHA and check name.
Duplicate same-named contexts fail closed; explicitly non-authoritative status
cannot replace the protected result. Provider API fallback is bounded and may
continue only when it preserves that same authority and subject binding.
