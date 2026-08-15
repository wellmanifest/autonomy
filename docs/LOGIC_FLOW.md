# Autonomous continuation logic

## Main state flow

```mermaid
stateDiagram-v2
    [*] --> Dispatch
    Dispatch --> Claim: protected automatic delivery
    Dispatch --> Degraded: trigger silence
    Degraded --> Claim: missed-cycle receipt + independent recovery
    Claim --> Observe: idempotent lease acquired
    Observe --> Evidence
    Evidence --> Plan: fresh runnable candidate
    Evidence --> Waiting: no candidate / unknown
    Plan --> IntentCheckpoint: bounded scope + accepted base
    IntentCheckpoint --> GrantCheck: committed before implementation
    GrantCheck --> IsolatedEdit: active + in scope + budget
    GrantCheck --> Escalated: expired / revoked / excluded
    IsolatedEdit --> DeterministicValidate
    DeterministicValidate --> IndependentValidate: pass
    DeterministicValidate --> Repair: bounded failure
    IndependentValidate --> PublishPR: exact-head pass
    IndependentValidate --> Repair: bounded failure
    Repair --> IsolatedEdit: retry available
    Repair --> Escalated: retry exhausted
    PublishPR --> ExactHeadGate
    ExactHeadGate --> SuccessorPR: protected base changed
    SuccessorPR --> IntentCheckpoint: renew base; preserve predecessor
    ExactHeadGate --> IndependentValidate: candidate head changed
    ExactHeadGate --> PostApprovalConvergence: trusted approval
    PostApprovalConvergence --> PostApprovalConvergence: new/pending check; reset stability
    PostApprovalConvergence --> EffectReconcile: two stable reads + terminal success
    EffectReconcile --> ProtectedMerge: no authoritative effect exists
    EffectReconcile --> PostMergeVerify: exact effect already applied
    EffectReconcile --> Escalated: stale / ambiguous / closed-unmerged
    ProtectedMerge --> PostMergeVerify
    PostMergeVerify --> Checkpoint: read-back pass
    Checkpoint --> Continue: durable outcome
    PostMergeVerify --> Reaction: read-back fail
    Continue --> Dispatch: grant active
    Continue --> [*]: stop condition
    Waiting --> [*]
    Escalated --> [*]
    Reaction --> [*]
```

## Decision predicate

```text
AUTONOMOUS_MERGE_ALLOWED =
  trigger_or_recovery_receipt is fresh and origin-classified
  AND scheduler_heartbeat_status is independently evaluated
  AND provider_run > pre_dispatch_observation_boundary
  AND provider_run binds strategy + repository + target + head + correlation
  AND durable_claim is idempotently bound
  AND intent_checkpoint precedes implementation
  AND accepted_base = candidate.intent.accepted_base
  AND contract_consumers = {local, image, compose, hosted_ci, validator}
  AND every contract consumer resolved an exact allowlisted version and passed
  AND protected_registry_digest = resolved_registry_digest
  AND target_repository_outcome is isolated
  AND grant.active(now)
  AND kill_switch = enabled_value
  AND repository + branch + paths + actions are in scope
  AND classified_risk <= grant.risk_ceiling
  AND excluded_effects(change) = none
  AND measured_usage <= all budgets
  AND pull_request.same_repository
  AND pull_request.head = validation.head = approval.head
  AND pull_request.base = current_default_branch_head
  AND policy_digest = protected_policy_digest
  AND profile_digest = protected_profile_digest
  AND deterministic_checks = pass
  AND required_check_provenance uniquely matches protected registry
  AND independent_validator = pass
  AND approval_epoch > every merge-authorizing check inventory snapshot
  AND protected_registry = effective_repository_policy
  AND two stable protected reads bind the same complete required check set
  AND every post-approval required check = authoritative_terminal_success
  AND unresolved_critical_findings = 0
  AND implementer != validator != publisher
  AND external_effect_receipt is absent or exact already-applied
  AND native_platform_auto_merge = disabled
```

If any operand is false or unknown, merge is denied. Unknown never defaults to
permission.

## One-mutation controller cycle

```mermaid
sequenceDiagram
    participant C as Controller
    participant T as Trigger / Watchdog
    participant Q as Queue
    participant R as Registry
    participant O as Observer
    participant I as Implementer
    participant V as Validator App
    participant G as Git provider
    participant A as Audit

    T->>A: protected scheduler heartbeat
    C->>G: capture pre-dispatch provider run boundary
    T->>Q: automatic/recovery delivery with correlation
    C->>Q: claim idempotency tuple
    Q-->>C: durable lease + checkpoint
    C->>R: resolve repository execution policy
    R-->>C: digest-bound base/check/validator/merge bindings
    C->>Q: next runnable task
    Q-->>C: task + dependency/scope evidence
    C->>O: observe exact base and intent
    O-->>C: provenance-bound evidence
    C->>C: commit intent checkpoint before implementation
    C->>C: inventory and resolve every contract consumer
    C->>C: compile plan and check standing grant
    C->>I: bounded Process Envelope
    I-->>C: candidate head + tests + receipt
    C->>V: validate exact head + strategy + correlation after boundary
    V-->>G: bound trusted review/attestation
    C->>G: discover effective policy after approval
    G-->>C: approval-triggered checks + protected policy digest
    C->>G: wait for two stable terminal-success reads
    C->>G: rebind base, head, approval, policy, registry and checks
    C->>G: reconcile exact external effect receipt
    alt no authoritative effect
        C->>G: one mutation: merge
    else exact effect already applied
        G-->>C: existing approval + merge receipt; no mutation
    end
    G-->>C: merged SHA
    C->>A: append publication + read-back receipts
    C->>Q: checkpoint and close only after verified read-back
```

The next cycle may select the next task. Opening a PR, deleting a proven
equivalent superseded branch, explicitly closing a still-open PR, merging,
rolling back, or changing a ticket are separate requested mutations. A provider
may couple PR closure to the branch-delete operation; that is recorded as one
provider effect only after complete read-back, never treated as permission to
bundle another request. Unresolved work keeps both branch and open PR.

## Failure handling

| Condition | Required result |
|---|---|
| No fresh runnable item | `waiting` or `no_candidate`; no mutation |
| Primary trigger is silent | `degraded`; independent watchdog enqueues/reconciles a cycle |
| Heartbeat deadline plus grace expires | append a protected missed-cycle receipt and start/reconcile one bounded recovery |
| Manual or recovery dispatch succeeds | execution evidence only; scheduler liveness remains unproven until a new scheduler heartbeat |
| Scheduled delivery arrives after recovery | deduplicate against the same effect subject; no second review or merge |
| Duplicate delivery | reuse the idempotency tuple and resume from checkpoint; no duplicate effect |
| Candidate provider run is pre-boundary or lacks exact correlation bindings | reject it; workflow name, title and timing are not identity |
| Multiple post-boundary runs match incompletely | fail closed as ambiguous; do not select the newest by guess |
| Exact subject is externally merged with bound approval and merge receipt | return `already-applied`; reuse the authoritative receipt without another mutation |
| Subject is closed-unmerged, stale or lacks a trusted receipt | fail closed; it is not `already-applied` |
| Registry projection drifts | stop the affected repository before claim or publication |
| Effective ruleset/branch policy differs from registry | fail closed; repair the protected registry or repository policy before approval/merge |
| Unrelated matrix target fails | preserve aggregate failure visibility; do not block a passing target's own gates |
| Canary is stale or incomplete | operational conformance is false until a fresh automatic canary completes |
| Head changes after validation | invalidate approval and validate new head |
| Base changes before merge | preserve the candidate; open a successor PR from a renewed accepted base and revalidate every gate |
| Contract consumer is missing or resolves an unknown version | fail closed before that consumer executes |
| Same-named checks have ambiguous provenance | fail closed; do not count aggregate or non-authoritative status |
| Approval-triggered check is absent before review | defer only that circular check; require all non-circular checks to pass before approval |
| Approval triggers a new required check | require a fresh attempt after the approval timestamp, then two stable terminal-success reads before merge |
| First merge attempt precedes policy convergence | bounded retry is allowed only for unchanged head/base after convergence |
| Superseded branch has complete integrated lossless proof | request deletion while PR is open; read back branch absence, closed/unmerged state and preserved archive head; explicitly close later only if still open |
| Superseded branch has unresolved unique content | preserve branch and keep predecessor PR open as owner |
| Provider API is rate-limited | `degraded`; bounded fallback only with identical authority and subject bindings |
| Grant expires or is revoked | stop mutation, release lease, preserve evidence |
| Budget or retries exhausted | one deduplicated escalation receipt |
| Required check is missing/unknown | fail closed; never infer success |
| Read-back fails | reaction/rollback task; merged task remains unverified |
| Validator or publisher identity overlaps implementer | critical separation failure |
| Proposed policy/grant change | excluded effect; external authority required |
| Native auto-merge is enabled | block publication; require protected explicit App merge |

## Autonomy evolution

The fleet may propose improvements to its tools or policy, but those proposals
use a separate lifecycle: observe → candidate → canary → independent evidence →
external promotion. A green canary means promotion eligibility, not authority.
The default development grant never promotes its own new capability or widens
its own scope.
