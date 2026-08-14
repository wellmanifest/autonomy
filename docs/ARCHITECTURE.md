# Architecture and adoption

## Boundary

Wellmanifest publishes the policy contract. Subactor and Semcod implement it.
This prevents a standards repository from becoming a second runtime source of
truth.

```mermaid
flowchart TB
    WM[wellmanifest/autonomy\nstandard + schema + profile]
    Grant[External standing grant\nissuer + scope + expiry]
    Policy[Protected policy/profile store]
    Registry[Protected repository registry\nbase + checks + validator + merge]
    Trigger[Primary trigger + independent watchdog]
    Queue[Durable at-least-once queue\nclaim + checkpoint]
    Observer[Doctor + autonom + twin-probes\nread-only evidence]
    Planner[Planner / orchestrator\npropose-only]
    Edit[Repair or coding agent\nisolated branch]
    Validate[Independent validator\nexact head]
    Publish[Protected PR controller\nValidator App + merge]
    Audit[Receipts + read-back]

    WM --> Policy
    WM --> Registry
    Grant --> Policy
    Trigger --> Queue --> Observer --> Planner --> Edit --> Validate --> Publish --> Audit
    Registry --> Trigger
    Registry --> Validate
    Registry --> Publish
    Policy --> Planner
    Policy --> Edit
    Policy --> Validate
    Policy --> Publish
    Audit --> Queue
```

## Trust zones

The system has five relevant trust zones:

1. **Execution zone** — protected dispatcher, durable queue/checkpoint and a
   watchdog under a different principal; no candidate or merge authority.
2. **Candidate zone** — implementer checkout, no merge credentials, no live
   secret store, write access only to the ticket branch.
3. **Validation zone** — fresh checkout of exact head, protected test profile,
   no candidate write access, ability to emit only a verdict/attestation.
4. **Publication zone** — GitHub App or equivalent protected controller with
   narrowly scoped review and merge authority; no general coding role.
5. **Authority zone** — standing grant, revocation, policy/profile digest,
   repository registry, kill switch, and allowlists, all outside candidate and
   concurrently mutable development checkouts.

An LLM may participate in observation, planning, implementation, or advisory
review, but it does not move an operation between trust zones.

## Adoption contract

An adopter should place a manifest such as `.wellmanifest/autonomy.json` in the
project, while the protected controller stores or resolves an authoritative
copy of the grant and selected profile. The repository copy is reviewable
intent; the protected copy decides effects.

Recommended adoption order:

1. Pin `wellmanifest/autonomy` and the selected profile by immutable revision
   and digest.
2. Configure one durable at-least-once task queue, checkpoint store,
   idempotency keys, and deterministic runnable predicate.
3. Configure a protected primary trigger and an independently credentialed
   watchdog that recovers missed delivery.
4. Register exact agent principals and separate candidate, validation, and
   publication credentials/workspaces.
5. Compile all repository/base/check/validator/merge bindings from one protected
   digest-bound registry and reject projection drift.
6. Install protected required checks and a Validator App.
7. Start with observation-only and dry-run cycles.
8. Issue a short-lived grant for low-risk paths and a small change budget.
9. Prove automatic trigger delivery, recovery, exact-head validation, explicit
   App merge, read-back, branch cleanup, revocation, and rollback with a live
   low-risk canary. A manual dispatch does not satisfy this step.
10. Expand only through a new externally issued grant based on audit evidence.

## Subactor and Semcod mapping

The shipped profile maps existing products as follows:

| Stage | Primary products | Boundary |
|---|---|---|
| Dispatch/claim | `subactor/autonom` execution plane and protected watchdog | Durable at-least-once delivery; idempotent claim; manual runs are diagnostic only |
| Observe/evidence | `subactor/autonom`, `subactor/twin-probes`, `semcod/todo2code`, Code DSL/LSP | Read-only; claims retain provenance |
| Plan/queue | `subactor/orchestrator`, `subactor/skills-agent`, `semcod/planfile`, `semcod/todo2code` | Known capabilities and runnable tasks only |
| Implement | `subactor/repair-agent`, Autonom coding agent, `subactor/onedev-agent`, `semcod/koru`, bounded `semcod/repatch` | Isolated candidate branch; no approval identity |
| Validate | `subactor/validator-agent`, `subactor/autonomy-lab`, OneDev PR verifier, `semcod/vallm` and deterministic Semcod analyzers | Fresh exact-head checkout; LLM verdict advisory until protected attestation |
| Publish | Autonom PR controller, protected OneDev/GitHub App, `semcod/goal` | Same-repository PR, current base, trusted identity |
| Audit/continue | receipts, checkpoints, Planfile lifecycle, todo2code evidence graph | Verified close, deduplication, repository-isolated result, next runnable task |

`semcod/fixop` is not enabled for routine code autonomy because its
infrastructure effects cross the default excluded boundary. `semcod/heal`
provides redacted diagnosis only; arbitrary generated shell suggestions are not
an allowlisted capability. `semcod/repatch` is limited to declared UI files and
safety-validated patch options.

## Protected configuration

The following values must not be controlled solely by a candidate branch:

- grant status, issuer, scope, expiry, and revocation;
- selected profile digest and the single repository registry digest;
- base branches, required-check definitions, validator identities, and merge policies;
- trusted validator and publisher identities;
- branch protection/rulesets and native auto-merge disablement;
- primary trigger, queue/checkpoint, watchdog credential, and canary freshness;
- kill switch, cost budget, and credential bindings;
- validator attestation verification keys or issuer policy.

A repository PR may propose a change to these values, but that proposal is an
authority-policy change and is excluded from the default standing grant.

## Observed runtime reference: 2026-08-14

The first fresh Subactor canary was delivered by the user-level
`subactor-pr-controller.timer`; no person started the controller or the
Validator workflow. The controller used GitHub's `workflow_dispatch` transport
to invoke Validator, but the preceding durable trigger and claim receipts bind
the origin to `systemd-timer`, so `manual_dispatch=false` is justified by the
receipt chain rather than inferred from the transport name.

| Evidence | Immutable binding |
|---|---|
| Pull request | `subactor/autonom#13` |
| Trigger receipt | `0ddacec437cce96f08a8d918835665a1a07895864c0eaac3e49b4ce8791d0b1c` at `2026-08-14T17:21:03.130Z` |
| Exact operation | `subactor/autonom`, `ticket-006`, `autonom-ticket-006-liveness`, head `2f3071fd60002c68ac32878184bcb7633ab16d5e`, `protected-merge` |
| Idempotency/checkpoint key | `947bc4361a3861d415a69eff52f536316aede93e7401ef63e4268a2cd6a73557` |
| Protected registry | `sha256:b2da44c7da86c13b57eb378b6f105eb4e876778245e11b7002eece5eb52fad5e` |
| Validator run | `31823596201` |
| Exact-head App approval | review `4939687694`, `ifuri-validator-agent[bot]`, exact head above |
| Explicit App merge | merge commit `0d73709d04231b6ad7f9f6d07eb1f92d2fc42d37` at `2026-08-14T17:22:59Z` |
| Cleanup and canary | head branch deleted; canary receipt `fd960b35a9816246aec2629f619cf9ce42e68892fb8bab806697768f4ab795e2` |

This run proves primary-trigger delivery and a complete protected publication
path. It also exposed a deployment defect: its 15-minute claim lease did not
outlive the controller's 45-minute service timeout. That observation produced
the normative lease relation and filesystem durability/recovery rules in
Autonomy 0.2, followed by runtime hardening in `subactor/autonom#14`.

The next automatic timer cycle exercised that hardened runtime against exact
head `58665c0632c9b89f9db48a0a540910bb7a7152e9`. Claim
`aaa4a4018f50286027422cf1f53350082e4807954e0d5aa0ad7c94d273ba8a69`
was acquired at `2026-08-14T17:31:51.475Z` with expiry at
`2026-08-14T18:21:51.453Z`, giving a 50-minute lease for a service bounded to
45 minutes. Validator run `31824419531` approved the exact head in App review
`4939758197`, explicitly merged it as
`54b4bfce39e04603fbdfa84b83c302a2d497432e`, read the result back, deleted the
head branch and committed a checkpoint containing all eight underlying receipt
classes. This was live durability/publication evidence, not a replacement
liveness canary, because its correlation ID was not the configured canary ID.

The protected registry schedules an independent Validator watchdog for every
Subactor controller target, and deterministic tests cover the recovery policy.
No live missed-trigger watchdog recovery had been observed at this evidence
cut. Therefore this record alone MUST NOT be presented as full operational
conformance: that claim additionally requires a fresh canary under the hardened
lease and an observed independent watchdog recovery, as required by section 14.

## Protected-source isolation reference: 2026-08-14

A later controller cycle found that the shared `validator-agent` development
checkout had advanced two unmerged commits beyond protected `origin/main`,
changing the registry bytes from the pinned digest. The cycle at
`2026-08-14T17:48:20Z` rejected those bytes with
`protected_registry_digest_mismatch` and made zero mutations. The concurrent
commits were preserved rather than reset or copied into authority state.

Recovery created a detached authority-policy worktree at protected
`validator-agent@e1a128d79b97f812947e6f5cfc177e1b50762e14`, verified registry
digest `sha256:b2da44c7da86c13b57eb378b6f105eb4e876778245e11b7002eece5eb52fad5e`,
and changed the systemd policy input to that isolated path. The next automatic
timer successfully merged `subactor/autonom#16` through Validator run
`31826124333`, exact-head App review `4939909053`, merge
`814e2572e1e9889df847674bd2cb9c44d5f54858`, branch cleanup and checkpoint
`4c2519ef8d4c4a632907d570ddb4b7aba81aa7b8dc5e24e77cc9f611bc9c19ea`.

That deployment added systemd preflights, outside the Python controller, which
reject a dirty controller tree or a controller revision not contained in
protected `origin/main`. A subsequent automatic zero-mutation cycle at
`2026-08-14T17:59:10Z` passed both preflights before loading the controller.

Candidate worktree isolation alone is therefore insufficient. The running
execution plane and its authority inputs require separate deployment workspaces
that concurrent development cannot mutate implicitly. A controller self-check
cannot establish this boundary because the bytes being checked would also own
the decision.

## Exact-runtime rollout reference: 2026-08-14

The first 0.3 deployment still linked its user-level systemd service and timer
to the shared `subactor/autonom` checkout. While ticket-010 changed the unit on
its candidate branch, systemd resolved the new bytes before that pull request
was merged. The automatic timer start at `2026-08-14T18:47:10Z` therefore saw
the candidate unit's required exact-runtime pin without a deployed pin and
failed in `ExecStartPre`. No Python controller was loaded, no cycle receipt was
created and no external mutation was attempted. The fail-closed behavior was
correct; the linked supervisor source was not.

Recovery preserved the candidate branch and created the detached runtime
worktree `subactor/autonom@814e2572e1e9889df847674bd2cb9c44d5f54858`.
The service and timer were copied to the external user-systemd directory, the
runtime drop-in bound that exact SHA, and the service loaded Python only from
the detached path. The next natural timer cycle at
`2026-08-14T18:52:30.415Z` used that old protected runtime to process
`subactor/autonom#17` without a manual dispatch.

| Evidence | Immutable binding |
|---|---|
| Candidate | head `500862ed0ad486956a8e2c19d9e68a7f1f61a496`, ticket `ticket-010`, correlation `autonom-ticket-010-immutable-runtime-release` |
| Durable operation | checkpoint `c5ba6476482e20eaf0d1a01727cc9565cec977fe30c14712dd048eb4df3f85c0` |
| Validator | run `31830719505`, exact-head App review `4940318952` |
| Protected publication | App merge `88953aa58a48526caf1134ba40b04d0f39e3ff39` at `2026-08-14T18:54:24Z`; source branch deleted |
| Deployed execution plane | detached runtime and external pin both `88953aa58a48526caf1134ba40b04d0f39e3ff39` |
| Post-rollout proof | automatic `systemd-timer` cycle at `2026-08-14T18:57:40.427Z`; `ok=true`, `dry_run=false`, zero mutations |

The rollout prepared the new detached worktree before stopping the timer,
rejected foreign or dirty active deployments, quiesced the timer and service,
replaced the isolated worktree, copied supervisor units instead of linking
them, wrote the exact SHA outside the repository, reloaded systemd and resumed
the timer. Selecting the prior protected SHA through the same command is the
rollback path.

This incident distinguishes three properties that ancestry alone cannot
provide: exact byte selection, supervisor-source independence and a transition
boundary with effects stopped. Operational proof belongs to the first fresh
automatic cycle after that transition, not to the rollout command itself.

## Multi-surface contract migration reference: 2026-08-14

The Deployment standard migration supplied the practice evidence for Autonomy
0.5. Its first container image correctly selected the checker from an exact
schema allowlist, but the Compose service overrode that image command and still
invoked the legacy checker. The hosted workflow independently pinned the legacy
checker as well. A passing local dispatcher therefore did not prove that every
contract consumer had migrated.

The repair inventoried five separate surfaces: local CLI, container image
command, Compose override, hosted CI checkout, and independent Validator. Each
now resolves the manifest's exact `$schema` URI to one immutable supported
revision before executing it; an unknown version fails closed. The Compose
repair merged as `15ea7b123e4d09c424b70d74064b1a7910ef4715`, the hosted-CI
resolver as `4f211e82bcbe3c1435b067c396cb7fe4d1c2d749`, and the manifest
migration as `a13b6442545f5db3a6b1790a831641a1b888c7b2`. The final ticket
closure reached protected main at `6aab422b5e662815dcb911ffd81a412340864d76`.

During publication, protected `main` moved after an intent had accepted the
old base. Refreshing that binding required full validation. Reusing a published
branch through history replacement also created push and pull-request check
runs with the same displayed name. Autonomy 0.5 consequently chooses a new
successor PR, forbids standing-grant history rewrite, and identifies a required
check by protected producer, event, repository, exact head, and check name
rather than its displayed context alone.

The same session exhausted the provider's GraphQL budget while bounded REST
reads still returned exact-head check runs. That fallback was valid because it
preserved the provider authority and subject bindings. Rate limiting remained
a degraded observation; availability of a second API did not turn missing or
ambiguous evidence into success.
