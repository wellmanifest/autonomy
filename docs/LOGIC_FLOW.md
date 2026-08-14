# Autonomous continuation logic

## Main state flow

```mermaid
stateDiagram-v2
    [*] --> Observe
    Observe --> Evidence
    Evidence --> Plan: fresh runnable candidate
    Evidence --> Waiting: no candidate / unknown
    Plan --> GrantCheck
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
    ExactHeadGate --> IndependentValidate: head or base changed
    ExactHeadGate --> AutoMerge: current + trusted approval
    AutoMerge --> PostMergeVerify
    PostMergeVerify --> Continue: read-back pass
    PostMergeVerify --> Reaction: read-back fail
    Continue --> Observe: grant active
    Continue --> [*]: stop condition
    Waiting --> [*]
    Escalated --> [*]
    Reaction --> [*]
```

## Decision predicate

```text
AUTONOMOUS_MERGE_ALLOWED =
  grant.active(now)
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
  AND independent_validator = pass
  AND unresolved_critical_findings = 0
  AND implementer != validator != publisher
```

If any operand is false or unknown, merge is denied. Unknown never defaults to
permission.

## One-mutation controller cycle

```mermaid
sequenceDiagram
    participant C as Controller
    participant Q as Queue
    participant O as Observer
    participant I as Implementer
    participant V as Validator App
    participant G as Git provider
    participant A as Audit

    C->>Q: next runnable task
    Q-->>C: task + dependency/scope evidence
    C->>O: observe exact base and intent
    O-->>C: provenance-bound evidence
    C->>C: compile plan and check standing grant
    C->>I: bounded Process Envelope
    I-->>C: candidate head + tests + receipt
    C->>V: validate exact head under protected profile
    V-->>G: bound trusted review/attestation
    C->>G: re-read base, head and checks
    C->>G: one mutation: merge
    G-->>C: merged SHA
    C->>A: append publication + read-back receipts
    C->>Q: close only after verified read-back
```

The next cycle may select the next task. Opening a PR, closing a superseded PR,
merging, rolling back, or changing a ticket are separate mutations and must not
be bundled into the same controller cycle.

## Failure handling

| Condition | Required result |
|---|---|
| No fresh runnable item | `waiting` or `no_candidate`; no mutation |
| Head changes after validation | invalidate approval and validate new head |
| Base changes before merge | rebuild/rebase through an allowlisted path and revalidate |
| Grant expires or is revoked | stop mutation, release lease, preserve evidence |
| Budget or retries exhausted | one deduplicated escalation receipt |
| Required check is missing/unknown | fail closed; never infer success |
| Read-back fails | reaction/rollback task; merged task remains unverified |
| Validator or publisher identity overlaps implementer | critical separation failure |
| Proposed policy/grant change | excluded effect; external authority required |

## Autonomy evolution

The fleet may propose improvements to its tools or policy, but those proposals
use a separate lifecycle: observe → candidate → canary → independent evidence →
external promotion. A green canary means promotion eligibility, not authority.
The default development grant never promotes its own new capability or widens
its own scope.
